//+------------------------------------------------------------------+
//|                                                     Hydra.mq5    |
//|  Sistema de trading autónomo multi-estrategia para MetaTrader 5  |
//|  (probado para Exness, funciona en cualquier broker MT5).        |
//|                                                                  |
//|  Estrategias (todas en velas diarias, parámetros clásicos, no     |
//|  sobre-optimizados):                                             |
//|   D = Breakout Donchian 55/20 (Tortugas) con filtro EMA 50/200    |
//|   T = Momentum de series de tiempo (Moskowitz-Ooi-Pedersen 2012)  |
//|   M = Reversión a la media RSI(2) de Connors (índices y metales)  |
//|                                                                  |
//|  Aprendizaje: cada "brazo" (estrategia x símbolo) ajusta su       |
//|  riesgo entre 0.25x y 1.5x según la expectativa (en R) de sus     |
//|  últimos 30 trades. El historial se guarda en disco, así que      |
//|  sigue aprendiendo aunque reinicies MT5.                          |
//|                                                                  |
//|  La lógica es idéntica a trading-bot/backtest/backtest.py.        |
//+------------------------------------------------------------------+
#property copyright "Hydra"
#property version   "1.00"
#property description "Trend following + momentum + reversión a la media, con riesgo adaptativo."

#include <Trade\Trade.mqh>

enum ENUM_HYDRA_MODE
  {
   MODO_CONSERVADOR = 0, // Conservador: 0.5% por trade, 6% total
   MODO_NORMAL      = 1, // Normal: 1% por trade, 10% total
   MODO_RETO        = 2  // Reto $1M: 3% por trade, 20% total (sólo demo por defecto)
  };

input ENUM_HYDRA_MODE InpMode        = MODO_RETO;   // Modo de riesgo
input string InpSymbols              = "EURUSD,GBPUSD,USDJPY,AUDUSD,USDCAD,XAUUSD,XAGUSD,USOIL,US500,USTEC,US30,DE30,BTCUSD"; // Símbolos (se detecta el sufijo de Exness: m, c, etc.)
input double InpRiskOverride         = 0;     // % de riesgo por trade (0 = el del modo)
input double InpHeatOverride         = 0;     // % de riesgo total abierto (0 = el del modo)
input double InpKillDDOverride       = 0;     // % de drawdown que pausa entradas nuevas (0 = el del modo)
input double InpStartCapital         = 5000;    // Capital inicial del reto
input double InpGoal                 = 1000000; // Meta en dinero de la cuenta
input int    InpDelayMinutes         = 60;    // Minutos tras la apertura diaria antes de operar (evita spreads del rollover)
input bool   InpResetPeak            = false; // Reiniciar el máximo de capital guardado (úsalo si reinicias la demo)
input bool   InpLearning             = true;  // Aprendizaje adaptativo activado
input bool   InpAllowRetoOnReal      = false; // Permitir modo Reto en cuenta REAL
input bool   InpUseDonchian          = true;  // Estrategia D: Breakout Donchian
input bool   InpUseMomentum          = true;  // Estrategia T: Momentum
input bool   InpUseMeanRev           = true;  // Estrategia M: RSI(2)
input long   InpMagic                = 7700;  // Número mágico base (usa base, base+1, base+2)
input int    InpSlippagePoints       = 50;    // Deslizamiento máximo (puntos)

#define N_STRATS     3
#define LEARN_WINDOW 30
#define LEARN_MIN    8
#define DD_BRAKE     0.20   // con más de 20% de drawdown se opera a la mitad de riesgo
#define CLS_FX       0
#define CLS_METAL    1
#define CLS_ENERGY   2
#define CLS_INDEX    3
#define CLS_CRYPTO   4

string   g_codes[N_STRATS] = {"D", "T", "M"};
double   g_trailK[N_STRATS] = {2.5, 3.0, 0.0};
double   g_stopK[N_STRATS]  = {2.5, 3.0, 2.5};

string   g_sym[];        // nombre real en el broker (p. ej. EURUSDm)
string   g_base[];       // nombre base (EURUSD)
int      g_cls[];
datetime g_lastBar[];
int      g_nSym = 0;

double   g_risk, g_heat, g_killDD, g_lev;
string   g_learnKey[];   // historial de aprendizaje: brazo -> R
double   g_learnR[];
string   g_peakGV;
bool     g_paused = false;
CTrade   g_trade;

struct Ind
  {
   bool              ok;
   double            c, atr, dcHi, dcLo, exHi, exLo, sma200, sma5, ema50, ema200, rsi2, mom;
  };

//+------------------------------------------------------------------+
int OnInit()
  {
   switch(InpMode)
     {
      case MODO_CONSERVADOR: g_risk = 0.5; g_heat = 6;  g_killDD = 25; g_lev = 10; break;
      case MODO_NORMAL:      g_risk = 1.0; g_heat = 10; g_killDD = 35; g_lev = 20; break;
      default:               g_risk = 3.0; g_heat = 20; g_killDD = 60; g_lev = 30; break;
     }
   if(InpRiskOverride > 0)   g_risk = InpRiskOverride;
   if(InpHeatOverride > 0)   g_heat = InpHeatOverride;
   if(InpKillDDOverride > 0) g_killDD = InpKillDDOverride;

   bool isReal = (AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL);
   if(isReal && InpMode == MODO_RETO && !InpAllowRetoOnReal)
     {
      Alert("Hydra: el modo Reto está bloqueado en cuenta REAL. Usa Normal/Conservador o activa InpAllowRetoOnReal.");
      return(INIT_PARAMETERS_INCORRECT);
     }
   if(AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING)
      Print("Hydra: la cuenta es de tipo NETTING. Se operará sólo una estrategia por símbolo. Recomendado: cuenta Hedging.");

   string parts[];
   int n = StringSplit(InpSymbols, ',', parts);
   ArrayResize(g_sym, 0);
   ArrayResize(g_base, 0);
   ArrayResize(g_cls, 0);
   g_nSym = 0;
   for(int i = 0; i < n; i++)
     {
      string b = parts[i];
      StringTrimLeft(b);
      StringTrimRight(b);
      if(b == "")
         continue;
      string s = ResolveSymbol(b);
      if(s == "")
        {
         Print("Hydra: no encontré el símbolo ", b, " en este broker; se omite.");
         continue;
        }
      ArrayResize(g_sym, g_nSym + 1);
      ArrayResize(g_base, g_nSym + 1);
      ArrayResize(g_cls, g_nSym + 1);
      g_sym[g_nSym] = s;
      g_base[g_nSym] = b;
      g_cls[g_nSym] = ClassOf(b);
      g_nSym++;
     }
   ArrayResize(g_lastBar, g_nSym);
   ArrayInitialize(g_lastBar, 0);
   if(g_nSym == 0)
     {
      Alert("Hydra: ningún símbolo válido.");
      return(INIT_FAILED);
     }

   g_peakGV = "HYDRA_PEAK_" + IntegerToString(AccountInfoInteger(ACCOUNT_LOGIN));
   if(InpResetPeak || !GlobalVariableCheck(g_peakGV))
      GlobalVariableSet(g_peakGV, AccountInfoDouble(ACCOUNT_EQUITY));

   g_trade.SetDeviationInPoints(InpSlippagePoints);
   LoadLearning();
   EventSetTimer(30);
   Print("Hydra iniciado: ", g_nSym, " símbolos, riesgo ", g_risk, "%/trade, máximo abierto ", g_heat, "%.");
   OnTimer();
   return(INIT_SUCCEEDED);
  }

void OnDeinit(const int reason)
  {
   EventKillTimer();
   Comment("");
  }

//+------------------------------------------------------------------+
void OnTimer()
  {
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double peak = MathMax(GlobalVariableGet(g_peakGV), eq);
   GlobalVariableSet(g_peakGV, peak);
   double dd = (peak > 0) ? 1.0 - eq / peak : 0;
   g_paused = (dd * 100.0 >= g_killDD);

   for(int i = 0; i < g_nSym; i++)
     {
      datetime bar = iTime(g_sym[i], PERIOD_D1, 0);
      if(bar == 0 || bar == g_lastBar[i] || TimeCurrent() - bar < InpDelayMinutes * 60)
         continue;
      if(!MarketOpen(g_sym[i]))
         continue;              // se reintenta en el próximo timer
      if(ProcessSymbol(i, dd))
         g_lastBar[i] = bar;
     }
   DrawDashboard(eq, peak, dd);
  }

//+------------------------------------------------------------------+
//| Gestiona salidas y entradas de un símbolo con la vela diaria       |
//| recién cerrada. Devuelve false si faltan datos (se reintenta).     |
//+------------------------------------------------------------------+
bool ProcessSymbol(int i, double dd)
  {
   string sym = g_sym[i];
   Ind ind;
   if(!Compute(sym, ind))
      return(false);

   // ---- 1) gestionar posiciones abiertas
   for(int p = PositionsTotal() - 1; p >= 0; p--)
     {
      ulong ticket = PositionGetTicket(p);
      if(ticket == 0 || PositionGetString(POSITION_SYMBOL) != sym)
         continue;
      int st = (int)(PositionGetInteger(POSITION_MAGIC) - InpMagic);
      if(st < 0 || st >= N_STRATS)
         continue;
      int dir = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY) ? 1 : -1;
      double sl = PositionGetDouble(POSITION_SL);
      bool doClose = false;
      if(st == 0)
         doClose = (dir == 1 && ind.c < ind.exLo) || (dir == -1 && ind.c > ind.exHi);
      else if(st == 1)
         doClose = (dir == 1 && ind.mom <= 0) || (dir == -1 && ind.mom >= 0);
      else
        {
         int held = iBarShift(sym, PERIOD_D1, (datetime)PositionGetInteger(POSITION_TIME), false);
         doClose = (ind.c > ind.sma5) || (held >= 10);
        }
      g_trade.SetExpertMagicNumber(InpMagic + st);
      if(doClose)
        {
         g_trade.PositionClose(ticket);
         continue;
        }
      if(g_trailK[st] > 0)
        {
         int digits = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
         double nsl = NormalizeDouble(ind.c - dir * g_trailK[st] * ind.atr, digits);
         if((dir == 1 && nsl > sl) || (dir == -1 && (sl == 0 || nsl < sl)))
            g_trade.PositionModify(ticket, nsl, PositionGetDouble(POSITION_TP));
        }
     }

   // ---- 2) entradas nuevas
   if(g_paused)
      return(true);
   bool useStrat[N_STRATS];
   useStrat[0] = InpUseDonchian;
   useStrat[1] = InpUseMomentum;
   useStrat[2] = InpUseMeanRev;
   bool netting = (AccountInfoInteger(ACCOUNT_MARGIN_MODE) != ACCOUNT_MARGIN_MODE_RETAIL_HEDGING);
   int cls = g_cls[i];

   for(int st = 0; st < N_STRATS; st++)
     {
      if(!useStrat[st] || HasPosition(sym, st))
         continue;
      if(netting && PositionSelect(sym))
         continue;
      int dir = Signal(st, ind, cls);
      if(dir == 0)
         continue;

      double eq = AccountInfoDouble(ACCOUNT_EQUITY);
      double mult = InpLearning ? LearnMult(ArmKey(i, st)) : 1.0;
      double brake = (dd > DD_BRAKE) ? 0.5 : 1.0;
      double riskMoney = eq * g_risk / 100.0 * mult * brake;
      if(OpenRisk() + riskMoney > eq * g_heat / 100.0)
         continue;

      double dist = g_stopK[st] * ind.atr;
      double lots = LotsFor(sym, riskMoney, dist, dir);
      if(lots <= 0)
         continue;

      MqlTick tick;
      if(!SymbolInfoTick(sym, tick))
         continue;
      int digits = (int)SymbolInfoInteger(sym, SYMBOL_DIGITS);
      double price = (dir == 1) ? tick.ask : tick.bid;
      double sl = NormalizeDouble(price - dir * dist, digits);
      double realRisk = LossPerLot(sym, dist) * lots;
      string cmt = StringFormat("HY|%s|%.2f", g_codes[st], realRisk);

      g_trade.SetExpertMagicNumber(InpMagic + st);
      g_trade.SetTypeFillingBySymbol(sym);
      bool ok = (dir == 1) ? g_trade.Buy(lots, sym, 0, sl, 0, cmt)
                : g_trade.Sell(lots, sym, 0, sl, 0, cmt);
      if(ok)
         PrintFormat("Hydra: %s %s %s %.2f lotes, SL %s, riesgo %.2f (x%.2f aprendizaje)",
                     g_codes[st], dir == 1 ? "COMPRA" : "VENTA", sym, lots,
                     DoubleToString(sl, digits), realRisk, mult);
      else
         PrintFormat("Hydra: falló orden %s %s: %d %s", g_codes[st], sym,
                     g_trade.ResultRetcode(), g_trade.ResultRetcodeDescription());
     }
   return(true);
  }

//+------------------------------------------------------------------+
int Signal(int st, const Ind &x, int cls)
  {
   bool canShort = (cls != CLS_INDEX);
   if(st == 0)
     {
      if(x.c > x.dcHi && x.ema50 > x.ema200)
         return(1);
      if(canShort && x.c < x.dcLo && x.ema50 < x.ema200)
         return(-1);
     }
   else if(st == 1)
     {
      if(x.mom >= 0.75 && x.c > x.ema50)
         return(1);
      if(canShort && x.mom <= -0.75 && x.c < x.ema50)
         return(-1);
     }
   else
     {
      if((cls == CLS_INDEX || cls == CLS_METAL) && x.c > x.sma200 && x.rsi2 < 10)
         return(1);
     }
   return(0);
  }

//+------------------------------------------------------------------+
//| Indicadores sobre la última vela diaria cerrada (igual que Python)|
//+------------------------------------------------------------------+
bool Compute(string sym, Ind &x)
  {
   x.ok = false;
   MqlRates r[];
   ArraySetAsSeries(r, false);
   int n = CopyRates(sym, PERIOD_D1, 1, 700, r);
   if(n < 300)
      return(false);
   int last = n - 1;

   double atr = r[0].high - r[0].low;
   for(int k = 1; k < n; k++)
     {
      double tr = MathMax(r[k].high - r[k].low,
                          MathMax(MathAbs(r[k].high - r[k - 1].close), MathAbs(r[k].low - r[k - 1].close)));
      atr += (tr - atr) / 20.0;
     }
   double e50 = r[0].close, e200 = r[0].close;
   for(int k = 1; k < n; k++)
     {
      e50  += (r[k].close - e50) * 2.0 / 51.0;
      e200 += (r[k].close - e200) * 2.0 / 201.0;
     }
   double up = 0, dn = 0;
   for(int k = 1; k < n; k++)
     {
      double d = r[k].close - r[k - 1].close;
      double u = MathMax(d, 0), w = MathMax(-d, 0);
      if(k == 1)
        {
         up = u;
         dn = w;
        }
      else
        {
         up += (u - up) / 2.0;
         dn += (w - dn) / 2.0;
        }
     }
   x.rsi2 = (dn == 0) ? 100.0 : 100.0 - 100.0 / (1.0 + up / dn);

   x.dcHi = -DBL_MAX;
   x.dcLo = DBL_MAX;
   for(int k = last - 55; k < last; k++)
     {
      x.dcHi = MathMax(x.dcHi, r[k].high);
      x.dcLo = MathMin(x.dcLo, r[k].low);
     }
   x.exHi = -DBL_MAX;
   x.exLo = DBL_MAX;
   for(int k = last - 20; k < last; k++)
     {
      x.exHi = MathMax(x.exHi, r[k].high);
      x.exLo = MathMin(x.exLo, r[k].low);
     }
   double s200 = 0, s5 = 0;
   for(int k = last - 199; k <= last; k++)
      s200 += r[k].close;
   for(int k = last - 4; k <= last; k++)
      s5 += r[k].close;

   int lb[4] = {21, 63, 126, 252};
   double mom = 0;
   for(int j = 0; j < 4; j++)
     {
      double ch = r[last].close / r[last - lb[j]].close - 1.0;
      mom += (ch > 0) ? 1 : ((ch < 0) ? -1 : 0);
     }

   x.c = r[last].close;
   x.atr = atr;
   x.ema50 = e50;
   x.ema200 = e200;
   x.sma200 = s200 / 200.0;
   x.sma5 = s5 / 5.0;
   x.mom = mom / 4.0;
   x.ok = (atr > 0);
   return(x.ok);
  }

//+------------------------------------------------------------------+
//| Tamaño de posición                                                 |
//+------------------------------------------------------------------+
double LossPerLot(string sym, double dist)
  {
   double tv = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE_LOSS);
   if(tv <= 0)
      tv = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_VALUE);
   double ts = SymbolInfoDouble(sym, SYMBOL_TRADE_TICK_SIZE);
   if(tv <= 0 || ts <= 0)
      return(0);
   return(dist / ts * tv);
  }

double LotsFor(string sym, double riskMoney, double dist, int dir)
  {
   double lpl = LossPerLot(sym, dist);
   if(lpl <= 0)
      return(0);
   double step = SymbolInfoDouble(sym, SYMBOL_VOLUME_STEP);
   double mn = SymbolInfoDouble(sym, SYMBOL_VOLUME_MIN);
   double mx = SymbolInfoDouble(sym, SYMBOL_VOLUME_MAX);
   double lots = riskMoney / lpl;

   // tope de apalancamiento nocional por posición (igual que el backtest)
   double eq = AccountInfoDouble(ACCOUNT_EQUITY);
   double price = (dir == 1) ? SymbolInfoDouble(sym, SYMBOL_ASK) : SymbolInfoDouble(sym, SYMBOL_BID);
   double notionalPerLot = LossPerLot(sym, price);
   if(notionalPerLot > 0)
      lots = MathMin(lots, eq * g_lev / MathMax(1.0, g_nSym / 4.0) / notionalPerLot);

   // nunca usar más del 50% del margen libre en una sola operación
   double margin = 0;
   ENUM_ORDER_TYPE type = (dir == 1) ? ORDER_TYPE_BUY : ORDER_TYPE_SELL;
   if(OrderCalcMargin(type, sym, 1.0, price, margin) && margin > 0)
      lots = MathMin(lots, AccountInfoDouble(ACCOUNT_MARGIN_FREE) * 0.5 / margin);

   lots = MathFloor(lots / step) * step;
   if(lots < mn)
     {
      if(mn * lpl <= riskMoney * 1.5)
         lots = mn;               // el lote mínimo arriesga a lo más 1.5x lo planeado
      else
         return(0);
     }
   lots = MathMin(lots, mx);
   int volDigits = (int)MathMax(0, MathCeil(-MathLog10(step)));
   return(NormalizeDouble(lots, volDigits));
  }

//+------------------------------------------------------------------+
//| Riesgo abierto total: lo que se perdería si todos los SL saltan    |
//+------------------------------------------------------------------+
double OpenRisk()
  {
   double total = 0;
   for(int p = PositionsTotal() - 1; p >= 0; p--)
     {
      ulong ticket = PositionGetTicket(p);
      if(ticket == 0)
         continue;
      long st = PositionGetInteger(POSITION_MAGIC) - InpMagic;
      if(st < 0 || st >= N_STRATS)
         continue;
      double open = PositionGetDouble(POSITION_PRICE_OPEN);
      double sl = PositionGetDouble(POSITION_SL);
      bool buy = (PositionGetInteger(POSITION_TYPE) == POSITION_TYPE_BUY);
      if(sl == 0)
         continue;
      double loss = buy ? open - sl : sl - open;
      if(loss > 0)
         total += LossPerLot(PositionGetString(POSITION_SYMBOL), loss) * PositionGetDouble(POSITION_VOLUME);
     }
   return(total);
  }

bool HasPosition(string sym, int st)
  {
   for(int p = PositionsTotal() - 1; p >= 0; p--)
     {
      ulong ticket = PositionGetTicket(p);
      if(ticket != 0 && PositionGetString(POSITION_SYMBOL) == sym &&
         PositionGetInteger(POSITION_MAGIC) == InpMagic + st)
         return(true);
     }
   return(false);
  }

//+------------------------------------------------------------------+
//| Aprendizaje: al cerrarse un trade se calcula su R y se guarda      |
//+------------------------------------------------------------------+
void OnTradeTransaction(const MqlTradeTransaction &trans, const MqlTradeRequest &req, const MqlTradeResult &res)
  {
   if(trans.type != TRADE_TRANSACTION_DEAL_ADD || !HistoryDealSelect(trans.deal))
      return;
   long st = HistoryDealGetInteger(trans.deal, DEAL_MAGIC) - InpMagic;
   if(st < 0 || st >= N_STRATS)
      return;
   ENUM_DEAL_ENTRY entry = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(trans.deal, DEAL_ENTRY);
   if(entry != DEAL_ENTRY_OUT && entry != DEAL_ENTRY_OUT_BY)
      return;
   long posId = HistoryDealGetInteger(trans.deal, DEAL_POSITION_ID);
   if(!HistorySelectByPosition(posId))
      return;

   double profit = 0, risk = 0;
   string sym = "";
   int dir = 0;
   bool closed = true;
   double vin = 0, vout = 0;
   for(int k = 0; k < HistoryDealsTotal(); k++)
     {
      ulong d = HistoryDealGetTicket(k);
      profit += HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_SWAP) +
                HistoryDealGetDouble(d, DEAL_COMMISSION);
      ENUM_DEAL_ENTRY e = (ENUM_DEAL_ENTRY)HistoryDealGetInteger(d, DEAL_ENTRY);
      if(e == DEAL_ENTRY_IN)
        {
         vin += HistoryDealGetDouble(d, DEAL_VOLUME);
         sym = HistoryDealGetString(d, DEAL_SYMBOL);
         dir = (HistoryDealGetInteger(d, DEAL_TYPE) == DEAL_TYPE_BUY) ? 1 : -1;
         string parts[];
         if(StringSplit(HistoryDealGetString(d, DEAL_COMMENT), '|', parts) == 3)
            risk = StringToDouble(parts[2]);
        }
      else
         vout += HistoryDealGetDouble(d, DEAL_VOLUME);
     }
   if(vout + 1e-9 < vin)
      closed = false;              // cierre parcial: se espera al final
   if(!closed || risk <= 0)
      return;

   double R = profit / risk;
   int idx = -1;
   for(int i = 0; i < g_nSym; i++)
      if(g_sym[i] == sym)
         idx = i;
   if(idx < 0)
      return;
   string key = ArmKey(idx, (int)st);
   AddLearning(key, R, true);
   Journal(sym, g_codes[st], dir, profit, R);
   PrintFormat("Hydra aprendió: %s cerró con %.2fR -> nuevo multiplicador x%.2f", key, R, LearnMult(key));
  }

string ArmKey(int idx, int st) { return(g_base[idx] + "_" + g_codes[st]); }

double LearnMult(string key)
  {
   double sum = 0;
   int cnt = 0;
   for(int k = ArraySize(g_learnKey) - 1; k >= 0 && cnt < LEARN_WINDOW; k--)
      if(g_learnKey[k] == key)
        {
         sum += g_learnR[k];
         cnt++;
        }
   if(cnt < LEARN_MIN)
      return(1.0);
   return(MathMax(0.25, MathMin(1.5, 1.0 + sum / cnt)));
  }

void AddLearning(string key, double R, bool persist)
  {
   int n = ArraySize(g_learnKey);
   ArrayResize(g_learnKey, n + 1);
   ArrayResize(g_learnR, n + 1);
   g_learnKey[n] = key;
   g_learnR[n] = R;
   if(!persist)
      return;
   int h = FileOpen("Hydra_learning.csv", FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(h == INVALID_HANDLE)
      return;
   FileSeek(h, 0, SEEK_END);
   FileWrite(h, key, DoubleToString(R, 4));
   FileClose(h);
  }

void LoadLearning()
  {
   ArrayResize(g_learnKey, 0);
   ArrayResize(g_learnR, 0);
   int h = FileOpen("Hydra_learning.csv", FILE_READ | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(h == INVALID_HANDLE)
      return;
   while(!FileIsEnding(h))
     {
      string key = FileReadString(h);
      if(FileIsEnding(h) && key == "")
         break;
      double R = StringToDouble(FileReadString(h));
      if(key != "")
         AddLearning(key, R, false);
     }
   FileClose(h);
   Print("Hydra: cargué ", ArraySize(g_learnKey), " trades de aprendizaje previos.");
  }

void Journal(string sym, string code, int dir, double profit, double R)
  {
   int h = FileOpen("Hydra_journal.csv", FILE_READ | FILE_WRITE | FILE_CSV | FILE_ANSI | FILE_COMMON, ',');
   if(h == INVALID_HANDLE)
      return;
   if(FileSize(h) == 0)
      FileWrite(h, "fecha", "simbolo", "estrategia", "direccion", "resultado", "R", "balance");
   FileSeek(h, 0, SEEK_END);
   FileWrite(h, TimeToString(TimeCurrent()), sym, code, dir == 1 ? "compra" : "venta",
             DoubleToString(profit, 2), DoubleToString(R, 2), DoubleToString(AccountInfoDouble(ACCOUNT_BALANCE), 2));
   FileClose(h);
  }

//+------------------------------------------------------------------+
//| Utilidades                                                        |
//+------------------------------------------------------------------+
string ResolveSymbol(string base)
  {
   if(SymbolSelect(base, true))
      return(base);
   int n = SymbolsTotal(false);
   for(int i = 0; i < n; i++)
     {
      string s = SymbolName(i, false);
      if(StringFind(s, base) == 0 && StringLen(s) <= StringLen(base) + 2 && SymbolSelect(s, true))
         return(s);
     }
   return("");
  }

int ClassOf(string b)
  {
   if(StringFind(b, "XAU") == 0 || StringFind(b, "XAG") == 0 || StringFind(b, "XPT") == 0)
      return(CLS_METAL);
   if(StringFind(b, "OIL") >= 0 || StringFind(b, "BRENT") >= 0 || StringFind(b, "NGAS") >= 0)
      return(CLS_ENERGY);
   if(StringFind(b, "BTC") == 0 || StringFind(b, "ETH") == 0)
      return(CLS_CRYPTO);
   string idx[] = {"US500", "USTEC", "US30", "DE30", "DE40", "UK100", "JP225", "FR40", "AUS200", "HK50", "STOXX50"};
   for(int i = 0; i < ArraySize(idx); i++)
      if(b == idx[i])
         return(CLS_INDEX);
   return(CLS_FX);
  }

bool MarketOpen(string sym)
  {
   if(SymbolInfoInteger(sym, SYMBOL_TRADE_MODE) != SYMBOL_TRADE_MODE_FULL)
      return(false);
   MqlTick t;
   if(!SymbolInfoTick(sym, t))
      return(false);
   return(TimeCurrent() - t.time < 600);
  }

void DrawDashboard(double eq, double peak, double dd)
  {
   double start = InpStartCapital;
   double progress = (eq > start && InpGoal > start) ? MathLog(eq / start) / MathLog(InpGoal / start) * 100.0 : 0;
   int mine = 0;
   for(int p = PositionsTotal() - 1; p >= 0; p--)
      if(PositionGetTicket(p) != 0)
        {
         long st = PositionGetInteger(POSITION_MAGIC) - InpMagic;
         if(st >= 0 && st < N_STRATS)
            mine++;
        }
   string modes[3] = {"Conservador", "Normal", "Reto $1M"};
   string s = StringFormat("HYDRA  |  modo %s  |  %s\n", modes[InpMode], g_paused ? "PAUSADO por drawdown" : "operando");
   s += StringFormat("Capital: %.2f   Máximo: %.2f   Drawdown: %.1f%%\n", eq, peak, dd * 100);
   s += StringFormat("Meta: %.0f   Progreso (escala log): %.1f%%\n", InpGoal, progress);
   s += StringFormat("Posiciones abiertas: %d   Riesgo abierto: %.2f (%.1f%%)\n", mine, OpenRisk(), eq > 0 ? OpenRisk() / eq * 100 : 0);
   s += StringFormat("Trades aprendidos: %d\n", ArraySize(g_learnKey));
   Comment(s);
  }
//+------------------------------------------------------------------+

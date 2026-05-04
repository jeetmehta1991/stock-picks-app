#!/bin/bash
# Full Phase 1B run — 509 tickers, 5 batches, ~15 hours
# Run ONLY after owner has approved pre-test outputs
# Usage:
#   export ANTHROPIC_API_KEY=your_key_here
#   bash run_full.sh

export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

source /c/Users/jeetm/Github/stock-picks-app/.venv/Scripts/activate

# Guard: refuse to run if API key is not set
if [ -z "$ANTHROPIC_API_KEY" ]; then
  echo "ERROR: ANTHROPIC_API_KEY is not set."
  echo "Set it first: export ANTHROPIC_API_KEY=your_key_here"
  echo "Then re-run: bash run_full.sh"
  exit 1
fi

echo "API key: SET"
echo "Pre-populating cache index..."
python scripts/prepopulate_cache_index.py

echo ""
echo "Starting full Phase 1B — 5 batches simultaneously..."
echo "Estimated time: 12-15 hours. Disable laptop sleep before leaving."
echo ""

echo "Starting batch 1 (101 tickers: MMM to CVX)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers MMM,AOS,ABT,ABBV,ACN,ADBE,AMD,AES,AFL,A,APD,ABNB,AKAM,ALB,ARE,ALGN,ALLE,LNT,ALL,GOOGL,GOOG,MO,AMZN,AMCR,AEE,AAL,AEP,AXP,AIG,AMT,AWK,AMP,AME,AMGN,APH,ADI,ANSS,AON,APA,APO,AMAT,APTV,ACGL,ADM,ANET,AJG,AIZ,T,ATO,ADSK,ADP,AZO,AVB,AVY,AXON,BKR,BALL,BAC,BAX,BDX,BRK-B,BBY,TECH,BIIB,BLK,BX,BK,BA,BKNG,BWA,BSX,BMY,AVGO,BR,BRO,BF-B,BLDR,BG,CDNS,CZR,CPT,COF,CAH,KMX,CCL,CARR,CTLT,CAT,CBOE,CBRE,CDW,CE,COR,CNC,CNP,CF,CRL,SCHW,CHTR,CVX \
  --output-dir output_1b_batch1 \
  --no-git \
  --no-agents \
  > batch1.log 2>&1 &
echo "Batch 1 PID: $!"

echo "Starting batch 2 (101 tickers: CMG to FOXA)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers CMG,CB,CHD,CI,CINF,CTAS,CSCO,C,CFG,CLX,CME,CMS,KO,CTSH,CL,CMCSA,CMA,CAG,COP,ED,STZ,CEG,COO,CPRT,GLW,CPAY,CTVA,CSGP,COST,CTRA,CRWD,CCI,CSX,CMI,DHI,DHR,DRI,DVA,DAY,DE,DAL,XRAY,DVN,DXCM,FANG,DLR,DFS,DG,DLTR,D,DPZ,DOV,DOW,DHC,DTE,DUK,DD,EMN,ETN,EBAY,ECL,EIX,EW,EA,ELV,LLY,EMR,ENPH,ETR,EOG,EPAM,EQT,EFX,EQIX,EQR,ESS,EL,EG,EVRG,ES,EXC,EXPE,EXPD,EXR,XOM,FFIV,FDS,FICO,FAST,FRT,FDX,FIS,FITB,FSLR,FE,FI,F,FTNT,FTV,FOXA \
  --output-dir output_1b_batch2 \
  --no-git \
  --no-agents \
  > batch2.log 2>&1 &
echo "Batch 2 PID: $!"

echo "Starting batch 3 (101 tickers: FOX to MA)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers FOX,BEN,FCX,GRMN,IT,GE,GEHC,GEN,GNRC,GD,GIS,GM,GPC,GILD,GPN,GL,GS,HAL,HIG,HAS,HCA,DOC,HSIC,HSY,HES,HPE,HLT,HOLX,HD,HON,HRL,HST,HWM,HPQ,HUBB,HUM,HBAN,HII,IBM,IEX,IDXX,ITW,INCY,IR,PODD,INTC,ICE,IFF,IP,IPG,INTU,ISRG,IVZ,INVH,IQV,IRM,JBHT,JBL,JKHY,J,JNJ,JCI,JNPR,K,KVUE,KEY,KEYS,KMB,KIM,KMI,KKR,KLAC,KHC,KR,LHX,LH,LRCX,LW,LVS,LDOS,LEN,LII,LILLY,LIN,LYV,LKQ,LMT,L,LOW,LULU,LYB,MTB,MRO,MPC,MKTX,MAR,MMC,MLM,MAS,MA \
  --output-dir output_1b_batch3 \
  --no-git \
  --no-agents \
  > batch3.log 2>&1 &
echo "Batch 3 PID: $!"

echo "Starting batch 4 (101 tickers: MTCH to SWKS)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers MTCH,MKC,MCD,MCK,MDT,MRK,META,MET,MTD,MGM,MCHP,MU,MSFT,MAA,SPGI,MCO,MS,MOS,MSI,MSCI,NDAQ,NTAP,NFLX,NEM,NWSA,NWS,NEE,NKE,NI,NDSN,NSC,NOC,NCLH,NRG,NUE,NVR,NXPI,ORLY,OXY,ODFL,OMC,ON,OKE,ORCL,OTIS,OGN,PCAR,PKG,PANW,PH,PAYX,PAYC,PYPL,PNR,PEP,PFE,PCG,PM,PSX,PNW,PNC,POOL,PPG,PPL,PFG,PG,PGR,PLD,PRU,PEG,PSA,PHM,QRVO,QCOM,PWR,DGX,RL,RJF,RTX,O,REG,REGN,RF,RSG,RMD,RVTY,ROK,ROL,ROP,ROST,RCL,CRM,SBAC,SLB,STX,SRE,NOW,SHW,SPG,SWKS \
  --output-dir output_1b_batch4 \
  --no-git \
  --no-agents \
  > batch4.log 2>&1 &
echo "Batch 4 PID: $!"

echo "Starting batch 5 (105 tickers: SNA to EFA)..."
nohup python backtest/run_phase1a.py --phase 1b \
  --tickers SNA,SOLV,SO,LUV,SWK,SBUX,STT,STLD,STE,SYK,SYF,SNPS,SYY,TMUS,TGT,TEL,TDY,TFX,TER,TSLA,TXN,TXT,TMO,TJX,TSCO,TT,TDG,TRV,TRMB,TFC,TYL,TSN,USB,UDR,ULTA,UNH,UPS,URI,UNP,UAL,UHS,VLO,VTR,VLTO,VRSN,VRSK,VZ,VRTX,VFC,VTRS,VICI,V,VMC,WRB,GWW,WAB,WBA,WMT,DIS,WBD,WM,WAT,WEC,WFC,WELL,WST,WDC,WRK,WY,WHR,WTW,WYNN,XEL,XYL,YUM,ZBRA,ZBH,ZTS,SPY,QQQ,IWM,DIA,VTI,XLK,XLF,XLV,XLI,XLY,XLP,XLU,XLB,XLRE,VXX,TLT,HYG,LQD,IEF,SHY,GLD,SLV,GDX,USO,EEM,EFA \
  --output-dir output_1b_batch5 \
  --no-git \
  --no-agents \
  > batch5.log 2>&1 &
echo "Batch 5 PID: $!"

echo ""
echo "All 5 batches launched. Monitor with: tail -f batch1.log"
echo "When all complete, run: bash run_commit.sh full"

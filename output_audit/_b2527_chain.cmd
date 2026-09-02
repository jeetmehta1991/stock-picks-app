@echo off
cd /d C:\Users\jeetm\Github\stock-picks-app
set PYTHONPATH=.
set OPENBLAS_NUM_THREADS=1
set OMP_NUM_THREADS=1
set MKL_NUM_THREADS=1
"C:\Users\jeetm\Github\stock-picks-app\.venv\Scripts\python.exe" scripts\run_serial_chain.py --specs output_audit/b2527_icg_span9_spec.json output_audit/b2527_icg_span20_spec.json output_audit/b2527_icg_span50_spec.json output_audit/b2527_icg_span100_spec.json output_audit/b2527_icg_span150_spec.json output_audit/b2527_icg_mult1.5_spec.json output_audit/b2527_icg_lookback2_spec.json output_audit/b2527_icg_minq8_spec.json output_audit/b2527_icg_mult1.0_spec.json output_audit/b2527_icg_mult1.25_spec.json output_audit/b2527_icg_lookback3_spec.json output_audit/b2527_icg_lookback6_spec.json output_audit/b2527_icg_lookback8_spec.json output_audit/b2527_icg_minq6_spec.json output_audit/b2527_icg_minq3_spec.json output_audit/b2527_icg_minq2_spec.json >> "C:\Users\jeetm\Github\stock-picks-app\output_audit\b2527_chain_detached.log" 2>&1
exit /b %ERRORLEVEL%

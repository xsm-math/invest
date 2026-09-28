"""Command line entry point; invoke from the checked-out repository root."""
from pathlib import Path
import argparse,json
from .data import download
from .pipeline import run

def main():
    parser=argparse.ArgumentParser(description='Gold strategy research, USD GLD, historical simulation')
    sub=parser.add_subparsers(dest='command',required=True)
    d=sub.add_parser('download',help='Fetch historical GLD snapshot; no mock-data fallback')
    d.add_argument('--output',default='data/GLD.csv')
    r=sub.add_parser('run',help='Run strategies, rolling selection, diagnostics and report')
    r.add_argument('--config',default='configs/default.json')
    r.add_argument('--out',default='reports/generated')
    args=parser.parse_args()
    if args.command=='download':download(Path(args.output))
    else:
        cfg=json.loads(Path(args.config).read_text(encoding='utf-8'))
        if not Path(cfg['data_path']).exists():
            parser.error('Market data is absent. Run: python -m gold_research download (or provide your CSV).')
        run(cfg,args.out)

import argparse
import json
from pathlib import Path

from deskreject.pipeline import audit


def main():
    parser = argparse.ArgumentParser(prog="deskreject")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    audit_parser = subparsers.add_parser("audit", help="Audit a PDF file")
    audit_parser.add_argument("pdf", help="Path to the PDF file")
    audit_parser.add_argument("--preset", required=True, help="Preset ID")
    audit_parser.add_argument("--tex", help="Path to the LaTeX source file")
    audit_parser.add_argument("--json", help="Path to output JSON file")
    audit_parser.add_argument("--no-vision", action="store_true", help="Disable vision checks")
    audit_parser.add_argument("--no-cache", action="store_true", help="Disable vision cache")
    
    args = parser.parse_args()
    
    if args.command == "audit":
        tex_text = None
        if args.tex:
            tex_path = Path(args.tex)
            if tex_path.exists():
                tex_text = tex_path.read_text(encoding="utf-8")
                
        report = audit(
            pdf_path=args.pdf,
            preset_id=args.preset,
            tex_text=tex_text,
            use_cache=not args.no_cache
        )
        
        report_dict = report.model_dump()
        
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                json.dump(report_dict, f, indent=2)
            print(f"Report written to {args.json}")
        else:
            print(json.dumps(report_dict, indent=2))
            
if __name__ == "__main__":
    main()

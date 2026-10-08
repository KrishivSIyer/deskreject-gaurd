import argparse

from deskreject.pipeline import audit


def main():
    parser = argparse.ArgumentParser(prog="deskreject")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    audit_parser = subparsers.add_parser("audit")
    audit_parser.add_argument("pdf", help="Path to PDF file")
    audit_parser.add_argument("--preset", required=True, help="Preset ID")
    audit_parser.add_argument("--tex", help="Optional TeX file path")
    audit_parser.add_argument("--json", help="Output JSON file path")
    audit_parser.add_argument("--no-vision", action="store_true", help="Disable vision")
    audit_parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    
    args = parser.parse_args()
    
    if args.command == "audit":
        tex_text = None
        if args.tex:
            with open(args.tex, "r", encoding="utf-8") as f:
                tex_text = f.read()
                
        report = audit(
            pdf_path=args.pdf,
            preset_id=args.preset,
            tex_text=tex_text,
            use_cache=not args.no_cache
        )
        
        report_json = report.model_dump_json(indent=2)
        if args.json:
            with open(args.json, "w", encoding="utf-8") as f:
                f.write(report_json)
        else:
            print(report_json)

if __name__ == "__main__":
    main()

import sys
import json
import gc

def main():
    if len(sys.argv) < 3:
        sys.exit(1)
        
    report_path = sys.argv[1]
    serialized_data = sys.argv[2]
    
    try:
        from src.pdf_generator import PdfReportGenerator
        
        records = json.loads(serialized_data)
        generator = PdfReportGenerator(report_path)
        
        generator.write_data_stream(records)
        generator.save()
        
        del generator
        gc.collect()
        sys.exit(0)
    except Exception as e:
        print(f"Worker Error: {e}", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()



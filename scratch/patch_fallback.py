import re

with open('ui/components.py', 'r', encoding='utf-8') as f:
    content = f.read()

fallback_func = '''def generate_fallback_summary(report) -> str:
    categories = set()
    for f in report.findings:
        if f.check == "statements":
            categories.add("missing mandatory statements (like data availability, ethics, or conflict of interest)")
        elif f.check == "figure_caption":
            categories.add("mismatches between figure images and their captions")
        elif f.check == "anonymity" or "ANON" in f.code:
            categories.add("identifying information that breaks double-blind anonymity")
        elif f.check == "sequencing" or "SEQ" in f.code:
            categories.add("figures being mentioned out of order or never referenced in the text")
        elif f.check == "legibility" or "LEG" in f.code:
            categories.add("blurry or low-resolution images that are hard to read")
        elif f.check == "accessibility" or "ACC" in f.code:
            if "CB" in f.code or "colorblind" in f.title.lower():
                categories.add("charts with colors that are indistinguishable for colorblind readers")
            else:
                categories.add("accessibility issues in your figures")
        else:
            categories.add(f.title.lower())
            
    cats = list(categories)
    if not cats:
        return "No errors found. The manuscript is good to go!"
        
    if len(cats) == 1:
        issues_str = cats[0]
    elif len(cats) == 2:
        issues_str = f"{cats[0]} and {cats[1]}"
    else:
        issues_str = ", ".join(cats[:-1]) + f", and {cats[-1]}"
        
    return f"We found several issues that need your attention before submitting. Specifically, there are problems with {issues_str}. These are the errors to be fixed and then you are good to go."

def generate_findings_summary(report: Report) -> str:'''

# Replace the start of generate_findings_summary to inject the fallback generator
content = content.replace('def generate_findings_summary(report: Report) -> str:', fallback_func)

# Now replace the except block
except_block = '''    except Exception as e:  # noqa: BLE001
        print(f"LLM Timeout/Error: {e}")
        return generate_fallback_summary(report)'''

content = re.sub(r'    except Exception as e:.*?return f"Could not generate AI summary: {e}"', except_block, content, flags=re.DOTALL)

with open('ui/components.py', 'w', encoding='utf-8') as f:
    f.write(content)

with open('src/components/JarDownloadHero.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# remove duplicate ending
if 'import { ChangelogSection } from \'./ChangelogSection\';' not in code:
    code = "import { ChangelogSection } from './ChangelogSection';\n" + code

# Clean up trailing parts
# Let's find the buttons grid end and replace cleanly
idx = code.rfind('</button>\n      </div>')
if idx != -1:
    end_part = """      </div>

      {/* Changelog Section */}
      <div className="mt-12">
        <ChangelogSection />
      </div>
    </div>
  );
};"""
    code = code[:idx + len('</button>\n      </div>')] + end_part

with open('src/components/JarDownloadHero.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Fixed JarDownloadHero.tsx successfully!")

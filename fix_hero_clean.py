with open('src/components/JarDownloadHero.tsx', 'r', encoding='utf-8') as f:
    code = f.read()

# Let's find where the navigation buttons start and replace from there to end
marker = "        <button\n          onClick={() => onNavigateTab('sources')"
idx = code.find(marker)
if idx != -1:
    clean_end = """        <button
          onClick={() => onNavigateTab('sources')}
          className="flex items-center gap-4 p-4 rounded-xl bg-neutral-900/80 hover:bg-neutral-800/90 border border-neutral-800 text-left transition-all group cursor-pointer"
        >
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 text-blue-400 flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors">
              Просмотр исходного Java кода
            </div>
            <div className="text-xs text-neutral-400">Исходные классы веток v2.0.0 (18 классов) и v1.5.0 (14 классов)</div>
          </div>
        </button>
      </div>

      {/* Version History & Changelog */}
      <div className="mt-12">
        <ChangelogSection />
      </div>
    </div>
  );
};"""
    code = code[:idx] + clean_end

with open('src/components/JarDownloadHero.tsx', 'w', encoding='utf-8') as f:
    f.write(code)

print("Cleaned JarDownloadHero.tsx successfully!")

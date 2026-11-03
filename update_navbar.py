with open('src/components/Navbar.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

old_button = '''            <button
              onClick={() => setActiveTab('cannon')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                activeTab === 'cannon'
                  ? 'bg-neutral-800 text-amber-400 border border-neutral-700'
                  : 'text-neutral-400 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Box className="w-4 h-4 text-amber-400" />
              <span className="hidden sm:inline">3D Пушка</span>
              <span className="sm:hidden">3D</span>
            </button>'''

new_button = '''            <button
              onClick={() => setActiveTab('cannon')}
              className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors relative ${
                activeTab === 'cannon'
                  ? 'bg-amber-500/20 text-amber-300 border border-amber-500/50 shadow-sm shadow-amber-500/20'
                  : 'text-neutral-300 hover:text-white hover:bg-neutral-900'
              }`}
            >
              <Box className="w-4 h-4 text-amber-400" />
              <span className="hidden lg:inline font-semibold">Предпросмотр моделей</span>
              <span className="hidden sm:inline lg:hidden font-semibold">Модели 3D</span>
              <span className="sm:hidden font-semibold">Модели</span>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500 text-neutral-950 font-mono">
                3D
              </span>
            </button>'''

if old_button in text:
    text = text.replace(old_button, new_button)
    with open('src/components/Navbar.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Navbar updated successfully!")
else:
    print("Could not find exact old_button match, updating with regex or replacement")
    import re
    pattern = r'<button[^>]*onClick=\{\(\) => setActiveTab\(\'cannon\'\)\}.*?<\/button>'
    text = re.sub(pattern, new_button, text, flags=re.DOTALL)
    with open('src/components/Navbar.tsx', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Navbar updated with regex replacement!")

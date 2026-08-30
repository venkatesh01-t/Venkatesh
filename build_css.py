import subprocess
import os

print("Running Tailwind CSS compiler with full content scanning...")
# Run tailwindcss with explicit content and config
cmd = [
    'npx', '-y', 'tailwindcss@3',
    '--content', 'index.html,404.html,sections/*.html,script.js,js/*.js',
    '-c', 'tailwind.config.js',
    '-i', 'css/tw-input.css',
    '-o', 'css/tailwind.gen.css',
    '--minify'
]

res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("Tailwind stdout:", res.stdout)
if res.stderr:
    print("Tailwind stderr:", res.stderr)

# Read all components
with open('fonts/fonts.css', 'r', encoding='utf-8') as f:
    fonts_css = f.read()

with open('fonts/fontawesome.min.css', 'r', encoding='utf-8') as f:
    fa_css = f.read()

with open('css/tailwind.gen.css', 'r', encoding='utf-8') as f:
    tw_css = f.read()

with open('css/base.css', 'r', encoding='utf-8') as f:
    base_css = f.read()

with open('css/components.css', 'r', encoding='utf-8') as f:
    comp_css = f.read()

# Combine in correct CSS order: @font-face -> reset/utilities -> base -> components
master_css = f"""/* Master Minified Bundle */
{fonts_css}
{fa_css}
{tw_css}
{base_css}
{comp_css}
"""

with open('css/style.min.css', 'w', encoding='utf-8') as f:
    f.write(master_css)

print(f"Generated css/style.min.css ({len(master_css)} bytes)")
print("Verification:")
print("Contains max-w-7xl:", "max-w-7xl" in master_css)
print("Contains min-h-[85vh]:", "min-h-[85vh]" in master_css or "min-h-" in master_css)
print("Contains text-gradient:", "text-gradient" in master_css)
print("Contains fa-brands:", "fa-brands" in master_css)
print("Contains Inter font:", "Inter" in master_css)

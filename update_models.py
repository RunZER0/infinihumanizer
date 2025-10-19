#!/usr/bin/env python
"""Update HTML template to add Claude (OXO) model"""

with open('humanizer/templates/humanizer/humanizer.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the model cards section and replace it
output_lines = []
i = 0
while i < len(lines):
    # Look for the start of model selection
    if 'model-card selected' in lines[i] and 'deepseek' in lines[i]:
        # Skip old model cards until we find the closing div
        output_lines.append('            <label class="model-card" data-engine="deepseek">\n')
        output_lines.append('                <input type="radio" name="engine" value="deepseek">\n')
        output_lines.append('                <div class="model-header">\n')
        output_lines.append('                    <div class="model-left">\n')
        output_lines.append('                        <span class="model-icon">🔥</span>\n')
        output_lines.append('                        <span class="model-name">Loly</span>\n')
        output_lines.append('                    </div>\n')
        output_lines.append('                    <div class="model-badge">Beat Detectors</div>\n')
        output_lines.append('                </div>\n')
        output_lines.append('                <div class="model-description">Optimized to bypass AI detection systems</div>\n')
        output_lines.append('            </label>\n')
        output_lines.append('            \n')
        output_lines.append('            <label class="model-card selected" data-engine="claude">\n')
        output_lines.append('                <input type="radio" name="engine" value="claude" checked>\n')
        output_lines.append('                <div class="model-header">\n')
        output_lines.append('                    <div class="model-left">\n')
        output_lines.append('                        <span class="model-icon">⭕</span>\n')
        output_lines.append('                        <span class="model-name">OXO</span>\n')
        output_lines.append('                    </div>\n')
        output_lines.append('                    <div class="model-badge">Balanced</div>\n')
        output_lines.append('                </div>\n')
        output_lines.append('                <div class="model-description">Perfect balance of quality and authenticity</div>\n')
        output_lines.append('            </label>\n')
        output_lines.append('            \n')
        output_lines.append('            <label class="model-card" data-engine="openai">\n')
        output_lines.append('                <input type="radio" name="engine" value="openai">\n')
        output_lines.append('                <div class="model-header">\n')
        output_lines.append('                    <div class="model-left">\n')
        output_lines.append('                        <span class="model-icon">⚡</span>\n')
        output_lines.append('                        <span class="model-name">Smurk</span>\n')
        output_lines.append('                    </div>\n')
        output_lines.append('                    <div class="model-badge">Best Quality</div>\n')
        output_lines.append('                </div>\n')
        output_lines.append('                <div class="model-description">Highest quality output with natural errors</div>\n')
        output_lines.append('            </label>\n')
        
        # Skip the old model cards
        while i < len(lines) and not (lines[i].strip() == '</div>' and 'sidebar-section' in lines[i-1]):
            i += 1
        i -= 1  # Back up one so we don't skip the closing div
    else:
        output_lines.append(lines[i])
    i += 1

# Write the updated file
with open('humanizer/templates/humanizer/humanizer.html', 'w', encoding='utf-8') as f:
    f.writelines(output_lines)

print("✅ HTML template updated successfully!")
print("   - Added Claude (OXO) as second option (default)")
print("   - Updated descriptions:")
print("      • Loly: Beat Detectors")
print("      • OXO: Balanced")
print("      • Smurk: Best Quality")

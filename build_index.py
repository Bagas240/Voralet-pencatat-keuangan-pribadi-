import os
import shutil
import sys

from parts.part1_head import HTML_HEAD
from parts.part2_icons import PART2_ICONS
from parts.part3_services import PART3_SERVICES
from parts.part4_auth_pin import PART4_AUTH_PIN
from parts.part5_debts_milestones import PART5_DEBTS_MILESTONES
from parts.part6_modals import PART6_MODALS
from parts.part7_views import PART7_VIEWS
from parts.part8_app import PART8_APP

full_html = "".join([
    HTML_HEAD,
    PART2_ICONS,
    PART3_SERVICES,
    PART4_AUTH_PIN,
    PART5_DEBTS_MILESTONES,
    PART6_MODALS,
    PART7_VIEWS,
    PART8_APP
])

# Write to root index.html
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

# Write to Android assets folder
os.makedirs('app/src/main/assets', exist_ok=True)
with open('app/src/main/assets/index.html', 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"Successfully generated index.html: {len(full_html)} chars, {len(full_html.splitlines())} lines.")

import hashlib
import hmac
import os
import struct
import subprocess
import zlib

VERSION_PLACEHOLDER = '__VORALET_VERSION__'

# Split obfuscated vault shards matching AssetVaultDecryptor.kt
_SHARD_A = [
    0x79, 0x2F, 0x7A, 0x62, 0x47, 0x6F, 0x52, 0x79,
    0x7D, 0x6D, 0x5C, 0x45, 0x5F, 0x40, 0x7E, 0x2F,
    0x22, 0x51, 0x71, 0x3D, 0x52, 0x26, 0x2E, 0x65,
    0x48, 0x3A, 0x6B, 0x42, 0x76, 0x59, 0x2D, 0x5B,
]
_SHARD_B = [
    0x2F, 0x40, 0x28, 0x23, 0x2B, 0x2A, 0x37, 0x0D,
    0x22, 0x2B, 0x2A, 0x2C, 0x33, 0x34, 0x10, 0x4C,
    0x41, 0x39, 0x1E, 0x5E, 0x37, 0x45, 0x4A, 0x0B,
    0x20, 0x5C, 0x0D, 0x37, 0x17, 0x3F, 0x49, 0x33,
]
_VAULT_MAGIC = b'VRLT1'


def resolve_version():
    explicit_version = os.getenv('VORALET_VERSION')
    if explicit_version:
        return explicit_version.lstrip('v')

    github_ref = os.getenv('GITHUB_REF', '')
    if github_ref.startswith('refs/tags/'):
        return github_ref.removeprefix('refs/tags/').lstrip('v')

    try:
        import re
        gradle_path = os.path.join('app', 'build.gradle.kts')
        if os.path.isfile(gradle_path):
            with open(gradle_path, 'r', encoding='utf-8') as f:
                m = re.search(r'versionName\s*=\s*"([^"]+)"', f.read())
                if m:
                    return m.group(1).lstrip('v')
    except OSError:
        pass

    return '3.6.0'


def _rotl32(v: int, n: int) -> int:
    return ((v << n) | (v >> (32 - n))) & 0xFFFFFFFF


def _quarter_round(x: list, a: int, b: int, c: int, d: int):
    x[a] = (x[a] + x[b]) & 0xFFFFFFFF
    x[d] = _rotl32(x[d] ^ x[a], 16)
    x[c] = (x[c] + x[d]) & 0xFFFFFFFF
    x[b] = _rotl32(x[b] ^ x[c], 12)
    x[a] = (x[a] + x[b]) & 0xFFFFFFFF
    x[d] = _rotl32(x[d] ^ x[a], 8)
    x[c] = (x[c] + x[d]) & 0xFFFFFFFF
    x[b] = _rotl32(x[b] ^ x[c], 7)


def _chacha20_block(key: bytes, counter: int, nonce: bytes) -> bytes:
    state = [
        0x61707865,
        0x3320646E,
        0x79622D32,
        0x6B206574,
        *struct.unpack('<8I', key),
        counter & 0xFFFFFFFF,
        *struct.unpack('<3I', nonce),
    ]
    working = list(state)
    for _ in range(10):
        _quarter_round(working, 0, 4, 8, 12)
        _quarter_round(working, 1, 5, 9, 13)
        _quarter_round(working, 2, 6, 10, 14)
        _quarter_round(working, 3, 7, 11, 15)
        _quarter_round(working, 0, 5, 10, 15)
        _quarter_round(working, 1, 6, 11, 12)
        _quarter_round(working, 2, 7, 8, 13)
        _quarter_round(working, 3, 4, 9, 14)

    out_words = [(working[i] + state[i]) & 0xFFFFFFFF for i in range(16)]
    return struct.pack('<16I', *out_words)


def _chacha20_xor(key: bytes, nonce: bytes, initial_counter: int, data: bytes) -> bytes:
    out = bytearray(len(data))
    counter = initial_counter
    offset = 0
    total = len(data)
    while offset < total:
        keystream = _chacha20_block(key, counter, nonce)
        block_len = min(64, total - offset)
        for i in range(block_len):
            out[offset + i] = data[offset + i] ^ keystream[i]
        offset += block_len
        counter += 1
    return bytes(out)


def _stretch_key(seed: bytes, domain: bytes, rounds: int = 16) -> bytes:
    state = hashlib.sha256(seed + domain).digest()
    for r in range(rounds):
        state = hashlib.sha256(state + seed + domain + bytes([r & 0xFF])).digest()
    return state


def encrypt_vault_payload(html_text: str) -> bytes:
    raw_seed = bytes(
        (((a ^ b) + ((idx * 37 + 19) & 0xFF)) ^ ((idx * 13) & 0xFF)) & 0xFF
        for idx, (a, b) in enumerate(zip(_SHARD_A, _SHARD_B))
    )
    enc_key = _stretch_key(raw_seed, b'ENC_CHACHA20_V2')
    mac_key = _stretch_key(raw_seed, b'MAC_HMACSHA256_V2')

    compressed = zlib.compress(html_text.encode('utf-8'), 9)
    nonce = os.urandom(12)
    ciphertext = _chacha20_xor(enc_key, nonce, 1, compressed)
    tag = hmac.new(mac_key, _VAULT_MAGIC + nonce + ciphertext, hashlib.sha256).digest()
    return _VAULT_MAGIC + nonce + tag + ciphertext


from parts.part1_head import HTML_HEAD
from parts.part2_icons import PART2_ICONS
from parts.part3_services import PART3_SERVICES
from parts.part4_auth_pin import PART4_AUTH_PIN
from parts.part5_debts_milestones import PART5_DEBTS_MILESTONES
from parts.part6_modals import PART6_MODALS
from parts.part7_views import PART7_VIEWS
from parts.part8_app import PART8_APP


def transpile_jsx(raw_jsx):
    """
    Pre-transpile JSX into clean, native JavaScript at build time.
    Eliminates runtime Babel overhead and shrinks APK assets.
    """
    node_script = """
const fs = require('fs');
const vm = require('vm');
const babelPath = fs.existsSync('./vendor/babel.min.js')
    ? './vendor/babel.min.js'
    : './app/src/main/assets/vendor/babel.min.js';

if (!fs.existsSync(babelPath)) {
    process.stderr.write('Babel file not found at: ' + babelPath);
    process.exit(1);
}

const babelCode = fs.readFileSync(babelPath, 'utf8');
const sandbox = { window: {}, navigator: { userAgent: 'node' } };
vm.createContext(sandbox);
vm.runInContext(babelCode, sandbox);
const Babel = sandbox.Babel || sandbox.window.Babel;

let input = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
    try {
        const res = Babel.transform(input, { presets: ['react'], compact: true, comments: false });
        process.stdout.write(res.code);
    } catch (err) {
        process.stderr.write('Transpile error: ' + err.message);
        process.exit(1);
    }
});
"""
    try:
        proc = subprocess.Popen(
            ['node', '-e', node_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        out, err = proc.communicate(raw_jsx)
        if proc.returncode == 0 and out.strip():
            return out, True
        else:
            print(f"[Build Warning] Node transpile returned code {proc.returncode}: {err.strip()}")
            return raw_jsx, False
    except Exception as ex:
        print(f"[Build Warning] Could not run Node transpile: {ex}")
        return raw_jsx, False


def build():
    version = resolve_version()
    print(f"Building Voralet v{version}...")

    root_tag = '<div id="root"></div>'
    root_idx = HTML_HEAD.find(root_tag)
    if root_idx != -1:
        head_html = HTML_HEAD[:root_idx + len(root_tag)]
        script_part = HTML_HEAD[root_idx + len(root_tag):]
        tag_end = script_part.find('>') + 1
        head_js = script_part[tag_end:]
    else:
        head_html = HTML_HEAD
        head_js = ""

    app_js = PART8_APP
    script_close_idx = app_js.rfind('</script>')
    if script_close_idx != -1:
        app_code = app_js[:script_close_idx]
        closing_html = app_js[script_close_idx:]
    else:
        app_code = app_js
        closing_html = '\n  </script>\n</body>\n</html>\n'

    raw_jsx = head_js + PART2_ICONS + PART3_SERVICES + PART4_AUTH_PIN + PART5_DEBTS_MILESTONES + PART6_MODALS + PART7_VIEWS + app_code
    raw_jsx = raw_jsx.replace(VERSION_PLACEHOLDER, version)

    compiled_js, is_precompiled = transpile_jsx(raw_jsx)

    if is_precompiled:
        print("✓ JSX successfully pre-compiled to native ECMAScript! (Instant 0-lag startup)")
        full_html = head_html + '\n\n  <script>\n' + compiled_js + '\n' + closing_html
    else:
        print("[Notice] Using fallback mode.")
        full_html = "".join([
            HTML_HEAD,
            PART2_ICONS,
            PART3_SERVICES,
            PART4_AUTH_PIN,
            PART5_DEBTS_MILESTONES,
            PART6_MODALS,
            PART7_VIEWS,
            PART8_APP
        ]).replace(VERSION_PLACEHOLDER, version)

    # Write root & dist HTML for local web preview server.ts
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

    os.makedirs('dist', exist_ok=True)
    with open('dist/index.html', 'w', encoding='utf-8') as f:
        f.write(full_html)

    # Encrypt Android asset bundle so APK unzipping exposes no plain HTML/JS source
    assets_dir = os.path.join('app', 'src', 'main', 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    encrypted_vault = encrypt_vault_payload(full_html)
    vault_path = os.path.join(assets_dir, 'voralet_core.bin')
    with open(vault_path, 'wb') as f:
        f.write(encrypted_vault)

    plain_asset_html = os.path.join(assets_dir, 'index.html')
    if os.path.exists(plain_asset_html):
        os.remove(plain_asset_html)
        print("✓ Removed plaintext app/src/main/assets/index.html")

    print(
        f"Successfully generated encrypted Android vault ({len(encrypted_vault)} bytes) "
        f"from {len(full_html)} HTML chars ({len(full_html.splitlines())} lines)."
    )


if __name__ == '__main__':
    build()

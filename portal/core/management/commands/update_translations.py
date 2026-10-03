"""Collect translatable text and rebuild the translation files.

Django's own makemessages/compilemessages need the GNU gettext tools, which
aren't installed on Windows or on Render. This command does the same job in
pure Python:

  1. finds every {% translate %} / {% blocktranslate %} in the templates
     (using the same parser makemessages uses) and every gettext call in the
     Python code;
  2. updates locale/<lang>/LC_MESSAGES/django.po, keeping existing
     translations and dropping text that no longer exists;
  3. compiles each .po file into the .mo file Django reads.

Run it after changing any visible text:

    python manage.py update_translations

then fill in any new empty msgstr lines in the .po files and run it again.
Use --check to fail when something is untranslated (the tests do this).
"""

import ast
import re
from pathlib import Path

import polib
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.translation.template import templatize

APPS = ["core", "news", "ai", "games"]
PLURAL_FORMS = {
    "tr": "nplurals=2; plural=(n > 1);",
    "fr": "nplurals=2; plural=(n > 1);",
    "es": "nplurals=3; plural=n == 1 ? 0 : n != 0 && n % 1000000 == 0 ? 1 : 2;",
}
PYTHON_FUNCTIONS = {
    "_": "gettext",
    "gettext": "gettext",
    "gettext_lazy": "gettext",
    "gettext_noop": "gettext",
    "ngettext": "ngettext",
    "ngettext_lazy": "ngettext",
    "pgettext": "pgettext",
    "pgettext_lazy": "pgettext",
}
# templatize() turns template tags into calls like gettext(u'...') or
# gettext(u"...") (when the text has an apostrophe), and translated filter
# arguments such as default:_("...") into _("...").
_QUOTED = r"""u?(?:'(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")"""
TEMPLATE_CALL = re.compile(
    r"(?<![\w.])(gettext|ngettext|pgettext|npgettext|_)\(((?:\s*" + _QUOTED + r"\s*,?)+)"
)
TEMPLATE_STRING = re.compile(_QUOTED)


class Message:
    def __init__(self, msgid, plural=None, context=None):
        self.msgid, self.plural, self.context = msgid, plural, context
        self.locations = []

    @property
    def key(self):
        return (self.context, self.msgid)


def _add(messages, msgid, plural=None, context=None, location=None):
    message = messages.setdefault((context, msgid), Message(msgid, plural, context))
    if plural and not message.plural:
        message.plural = plural
    if location and location not in message.locations:
        message.locations.append(location)


def extract(base_dir):
    messages = {}
    for app in APPS:
        for path in sorted((base_dir / app).rglob("*")):
            location = (path.relative_to(base_dir).as_posix(), "")
            if path.suffix == ".html":
                _extract_template(path, messages, location)
            elif path.suffix == ".py" and "migrations" not in path.parts:
                _extract_python(path, messages, location)
    return messages


def _extract_template(path, messages, location):
    code = templatize(path.read_text(encoding="utf-8"), origin=str(path))
    for match in TEMPLATE_CALL.finditer(code):
        name = match.group(1)
        strings = [ast.literal_eval(s) for s in TEMPLATE_STRING.findall(match.group(2))]
        if name in ("gettext", "_"):
            _add(messages, strings[0], location=location)
        elif name == "ngettext":
            _add(messages, strings[0], strings[1], location=location)
        elif name == "pgettext":
            _add(messages, strings[1], context=strings[0], location=location)
        elif name == "npgettext":
            _add(messages, strings[1], strings[2], context=strings[0], location=location)


def _extract_python(path, messages, location):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        kind = PYTHON_FUNCTIONS.get(node.func.id)
        if kind is None:
            continue
        args = [a.value for a in node.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
        if kind == "gettext" and args:
            _add(messages, args[0], location=location)
        elif kind == "ngettext" and len(args) >= 2:
            _add(messages, args[0], args[1], location=location)
        elif kind == "pgettext" and len(args) >= 2:
            _add(messages, args[1], context=args[0], location=location)


class Command(BaseCommand):
    help = "Collect translatable text, update the .po files and compile the .mo files."

    def add_arguments(self, parser):
        parser.add_argument(
            "--check", action="store_true", help="Exit with an error if anything is untranslated."
        )

    def handle(self, *args, check=False, **options):
        base_dir = Path(settings.BASE_DIR)
        messages = extract(base_dir)
        self.stdout.write(f"Found {len(messages)} translatable messages.")

        missing_total = 0
        for language, _name in settings.LANGUAGES:
            if language == settings.LANGUAGE_CODE:
                continue
            missing = self._update(base_dir, language, messages)
            missing_total += len(missing)
            status = "complete" if not missing else f"{len(missing)} untranslated"
            self.stdout.write(f"  {language}: {status}")
            for msgid in missing[:20]:
                self.stdout.write(f"      - {msgid!r}")

        if check and missing_total:
            raise CommandError(f"{missing_total} messages are untranslated.")

    def _update(self, base_dir, language, messages):
        folder = base_dir / "locale" / language / "LC_MESSAGES"
        folder.mkdir(parents=True, exist_ok=True)
        po_path = folder / "django.po"
        old = polib.pofile(str(po_path)) if po_path.exists() else polib.POFile()
        old_entries = {(e.msgctxt, e.msgid): e for e in old}
        nplurals = int(PLURAL_FORMS[language].split(";")[0].split("=")[1])

        po = polib.POFile(wrapwidth=0)
        po.metadata = {
            "Project-Id-Version": "Kuzey's Aviation and History Portal",
            "Language": language,
            "MIME-Version": "1.0",
            "Content-Type": "text/plain; charset=UTF-8",
            "Content-Transfer-Encoding": "8bit",
            "Plural-Forms": PLURAL_FORMS[language],
        }
        missing = []
        for key in sorted(messages, key=lambda k: (k[0] or "", k[1])):
            message = messages[key]
            previous = old_entries.get(key)
            entry = polib.POEntry(
                msgid=message.msgid, msgctxt=message.context, occurrences=message.locations
            )
            if message.plural:
                entry.msgid_plural = message.plural
                forms = dict(previous.msgstr_plural) if previous and previous.msgstr_plural else {}
                entry.msgstr_plural = {i: forms.get(i, "") for i in range(nplurals)}
                if not all(entry.msgstr_plural.values()):
                    missing.append(message.msgid)
            else:
                entry.msgstr = previous.msgstr if previous else ""
                if not entry.msgstr:
                    missing.append(message.msgid)
            po.append(entry)

        po.save(str(po_path))
        po.save_as_mofile(str(folder / "django.mo"))
        return missing

#!/usr/bin/env python3
"""Точечные правки существующих файлов форка (ID в профиле, без рекламы)."""
import re
import sys
from pathlib import Path

ROOT = Path("TMessagesProj/src/main/java/org/telegram")
errors = []
applied = 0


def flex(anchor):
    return r"\s+".join(re.escape(t) for t in anchor.split())


def patch(rel, anchor, repl):
    global applied
    p = ROOT / rel
    if not p.exists():
        errors.append(f"{rel}: файл не найден")
        return
    s = p.read_text(encoding="utf-8")
    pat = re.compile(flex(anchor))
    n = len(pat.findall(s))
    if n != 1:
        errors.append(f"{rel}: якорь найден {n} раз (нужно 1): {anchor[:80]!r}")
        return
    s = pat.sub(lambda m: repl.replace("{ANCHOR}", m.group(0)), s, count=1)
    p.write_text(s, encoding="utf-8")
    applied += 1
    print(f"OK   {rel}: {anchor[:60]!r}")


# ==================== РЕКЛАМА ====================
patch("messenger/MessagesController.java",
      "public SponsoredMessagesInfo getSponsoredMessages(long dialogId) {",
      "{ANCHOR}\n        if (true /*KT_NOADS*/) return null;")

patch("messenger/video/VideoAds.java",
      "private void load() { if (loading || loaded) return;",
      "{ANCHOR}\n        if (true /*KT_NOADS*/) return;")

patch("ui/Adapters/DialogsSearchAdapter.java",
      "if (query == null || query.length() < 4 ||",
      "if (true /*KT_NOADS*/ || query == null || query.length() < 4 ||")

# ==================== ID В ПРОФИЛЕ ====================
PA = "ui/ProfileActivity.java"

patch(PA, "private int usernameRow;",
      "{ANCHOR}\n    private int idRow = -1; /*KT_ID*/")

patch(PA, "usernameRow = -1;",
      "{ANCHOR}\n        idRow = -1;")

patch(PA,
      "if (user != null && username != null) { usernameRow = rowCount++; }",
      "{ANCHOR}\n                idRow = rowCount++;")

patch(PA,
      "} else if (chatId != 0) { if (chatInfo != null && (!TextUtils.isEmpty(chatInfo.about) ||",
      "} else if (chatId != 0) {\n            if (true /*KT_ID*/ || chatInfo != null && (!TextUtils.isEmpty(chatInfo.about) ||")

patch(PA,
      "if (ChatObject.isPublic(currentChat)) { usernameRow = rowCount++; }",
      "{ANCHOR}\n                idRow = rowCount++;")

patch(PA,
      "} else if (position == phoneRow || position == locationRow || position == numberRow || position == birthdayRow) {",
      "} else if (position == phoneRow || position == locationRow || position == numberRow || position == birthdayRow || position == idRow) {")

patch(PA,
      "} else if (position == phoneRow) { String text; TLRPC.User user = getMessagesController().getUser(userId); String phoneNumber;",
      "} else if (position == idRow) {\n"
      "                        detailCell.setTextAndValue(ktIdValue(), ktIdLabel(), false);\n"
      "                    {ANCHOR}")

patch(PA,
      "private boolean processOnClickOrPress(final int position, final View view, final float x, final float y) { if (position == usernameRow || position == setUsernameRow) {",
      """private String ktIdValue() {
          if (userId != 0) return String.valueOf(userId);
          return ((currentChat != null && ChatObject.isChannel(currentChat)) ? "-100" : "-") + chatId;
      }

      private String ktIdLabel() {
          if (userId != 0) return "ID";
          return "ID (internal: " + chatId + ")";
      }

      private boolean processOnClickOrPress(final int position, final View view, final float x, final float y) {
          if (idRow != -1 && position == idRow) {
              AndroidUtilities.addToClipboard(ktIdValue());
              BulletinFactory.of(this).createCopyBulletin(ktIdValue(), resourcesProvider).show();
              return true;
          }
          if (position == usernameRow || position == setUsernameRow) {""")

print(f"\nПрименено правок: {applied}")
if errors:
    print("\nОШИБКИ:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

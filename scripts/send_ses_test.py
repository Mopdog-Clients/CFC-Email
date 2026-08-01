#!/usr/bin/env python3
"""Send a local CFC campaign HTML file as an internal Amazon SES test email.

The script uses only Python's standard library and curl. AWS credentials and
recipient groups belong in .email-test.env, which is intentionally ignored.
"""

from __future__ import annotations

import argparse
import base64
import html as html_module
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from email.message import EmailMessage
from email.policy import SMTP
from email.utils import format_datetime, formataddr, make_msgid
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".email-test.env"
SES_PATH = "/v2/email/outbound-emails"
GITHUB_CODE_BASE_URL = "https://github.com/Mopdog-Clients/CFC-Email/blob/main/"
LIVE_PREVIEW_BASE_URL = "https://cfc-emails.mopdogdigital.com/"
EMAIL_HOME_URL = "https://cfc-emails.mopdogdigital.com/"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
BODY_OPENING_TAG = re.compile(r"<body\b[^>]*>", re.IGNORECASE)


def load_local_environment(path: Path) -> None:
    """Load simple KEY=VALUE entries without overwriting shell environment."""
    if not path.is_file():
        return

    for number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].lstrip()
        key, separator, value = line.partition("=")
        if not separator or not key.strip():
            raise ValueError(f"Invalid .email-test.env entry on line {number}.")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


def required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ValueError(f"Missing {name}. Add it to {ENV_FILE.name}.")
    return value


def recipients_for_group(group: str) -> list[str]:
    group_variable = {
        "personal": "SES_TEST_PERSONAL_RECIPIENTS",
        "team": "SES_TEST_TEAM_RECIPIENTS",
    }[group]
    recipients = [
        item.strip()
        for item in required_environment(group_variable).split(",")
        if item.strip()
    ]
    invalid = [
        address for address in recipients if not EMAIL_PATTERN.fullmatch(address)
    ]
    if invalid:
        raise ValueError(f"Invalid email address in {group_variable}.")
    return recipients


def resolve_campaign_file(value: str) -> Path:
    candidate = Path(value).expanduser().resolve()
    try:
        candidate.relative_to(PROJECT_ROOT)
    except ValueError as error:
        raise ValueError(
            "The selected file must be inside the CFC-Email repository."
        ) from error
    if candidate.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("The selected file must be an HTML file.")
    if not candidate.is_file():
        raise ValueError("The selected HTML file does not exist.")
    return candidate


def subject_for_file(path: Path, subject: str | None) -> str:
    if subject:
        return subject.strip()
    return f"[TEST] CFC Email — {path.relative_to(PROJECT_ROOT)}"


def sender_name() -> str:
    name = (
        os.environ.get("SES_TEST_FROM_NAME", "CFC Email Test").strip()
        or "CFC Email Test"
    )
    if "\r" in name or "\n" in name:
        raise ValueError("SES_TEST_FROM_NAME must be a single line.")
    return name


def reply_to_address() -> str:
    reply_to = os.environ.get("SES_TEST_REPLY_TO_EMAIL", "").strip()
    if reply_to and not EMAIL_PATTERN.fullmatch(reply_to):
        raise ValueError("SES_TEST_REPLY_TO_EMAIL must be a valid email address.")
    return reply_to


def project_links(campaign_file: Path) -> tuple[str, str, str]:
    """Build GitHub and preview links from a campaign's repository path."""
    relative_path = quote(campaign_file.relative_to(PROJECT_ROOT).as_posix(), safe="/")
    return (
        GITHUB_CODE_BASE_URL + relative_path,
        LIVE_PREVIEW_BASE_URL + relative_path,
        EMAIL_HOME_URL,
    )


def add_team_message(html: str, team_message: str, campaign_file: Path) -> str:
    """Prepend a reviewer note and project links above the campaign content."""
    note = team_message.strip()
    note_html = ""
    if note:
        note_html = (
            '<div style="margin-top: 12px;">'
            + html_module.escape(note).replace("\n", "<br />")
            + "</div>"
        )
    code_url, preview_url, home_url = project_links(campaign_file)
    preface = f"""
      <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color: #f3f4f6;">
        <tr>
          <td align="center" style="padding: 30px;">
            <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="720" style="width: 100%; max-width: 720px; background-color: #ffffff; border: 1px solid #d1d5db;">
              <tr>
                <td style="padding: 24px 28px; color: #1f2937; font-family: Arial, sans-serif; font-size: 15px; line-height: 22px;">
                  <div style="color: #b42318; font-family: 'Courier New', Courier, monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.25px; line-height: 16px; text-transform: uppercase;">Mopdog Digital - Internal Test</div>
                  {note_html}
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="margin-top: 20px; border-top: 1px solid #d1d5db;">
                    <tr>
                      <td style="padding-top: 16px; color: #b42318; font-family: 'Courier New', Courier, monospace; font-size: 11px; font-weight: bold; letter-spacing: 1.25px; line-height: 16px; text-transform: uppercase;">Project Links</td>
                    </tr>
                    <tr>
                      <td style="padding-top: 8px; font-size: 14px; line-height: 20px;"><a href="{html_module.escape(code_url, quote=True)}" style="color: #1f2937; text-decoration: underline;">View Code</a>: <a href="{html_module.escape(code_url, quote=True)}" style="color: #274286; text-decoration: underline;">{html_module.escape(code_url, quote=True)}</a></td>
                    </tr>
                    <tr>
                      <td style="padding-top: 10px; font-size: 14px; line-height: 20px;"><a href="{html_module.escape(preview_url, quote=True)}" style="color: #1f2937; text-decoration: underline;">View a Live Preview</a>: <a href="{html_module.escape(preview_url, quote=True)}" style="color: #274286; text-decoration: underline;">{html_module.escape(preview_url, quote=True)}</a></td>
                    </tr>
                    <tr>
                      <td style="padding-top: 10px; font-size: 14px; line-height: 20px;"><a href="{html_module.escape(home_url, quote=True)}" style="color: #1f2937; text-decoration: underline;">CFC Email GitHub Repo</a>: <a href="{html_module.escape(home_url, quote=True)}" style="color: #274286; text-decoration: underline;">{html_module.escape(home_url, quote=True)}</a></td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td height="50" style="height: 50px; font-size: 0; line-height: 0; background: #ffffff; background-color: #ffffff;">&nbsp;</td>
        </tr>
      </table>
    """
    if BODY_OPENING_TAG.search(html):
        return BODY_OPENING_TAG.sub(
            lambda match: match.group(0) + preface, html, count=1
        )
    return preface + html


def raw_email(
    html: str,
    sender: str,
    display_name: str,
    reply_to: str,
    recipients: Iterable[str],
    subject: str,
    campaign_file: Path,
    team_message: str,
    include_team_panel: bool,
) -> bytes:
    message = EmailMessage(policy=SMTP)
    message["Date"] = format_datetime(datetime.now(timezone.utc))
    message["From"] = formataddr((display_name, sender))
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject
    message["Message-ID"] = make_msgid(domain=sender.rsplit("@", 1)[1])
    if reply_to:
        message["Reply-To"] = reply_to
    message["X-CFC-Email-Test"] = "true"
    text_content = (
        "This is an internal test of "
        + str(campaign_file.relative_to(PROJECT_ROOT))
        + ".\n"
    )
    if include_team_panel:
        if team_message.strip():
            text_content += "\nTeam note:\n" + team_message.strip() + "\n"
        code_url, preview_url, home_url = project_links(campaign_file)
        text_content += (
            "\nProject links:\n"
            + "Code: "
            + code_url
            + "\nLive preview: "
            + preview_url
            + "\nCFC Email home: "
            + home_url
            + "\n"
        )
    text_content += (
        "\nOpen this message in an HTML-capable email client to review the campaign."
    )
    message.set_content(text_content)
    html_content = (
        add_team_message(html, team_message, campaign_file)
        if include_team_panel
        else html
    )
    message.add_alternative(html_content, subtype="html")
    return message.as_bytes()


def send_with_ses(message: bytes, sender: str, recipients: list[str]) -> str:
    region = os.environ.get("AWS_REGION", "us-east-1").strip() or "us-east-1"
    access_key = required_environment("AWS_ACCESS_KEY_ID")
    secret_key = required_environment("AWS_SECRET_ACCESS_KEY")
    session_token = os.environ.get("AWS_SESSION_TOKEN", "").strip()
    payload = json.dumps(
        {
            "Destination": {"ToAddresses": recipients},
            "Content": {"Raw": {"Data": base64.b64encode(message).decode("ascii")}},
        },
        separators=(",", ":"),
    ).encode("utf-8")
    if any(character in f"{access_key}{secret_key}" for character in ("\n", "\r", '"')):
        raise ValueError("AWS credentials contain an unsupported character.")

    credentials_file = tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", delete=False
    )
    try:
        os.chmod(credentials_file.name, 0o600)
        credentials_file.write(f'user = "{access_key}:{secret_key}"\n')
        credentials_file.close()
        command = [
            "curl",
            "--config",
            credentials_file.name,
            "--aws-sigv4",
            f"aws:amz:{region}:ses",
            "--fail-with-body",
            "--silent",
            "--show-error",
            "--request",
            "POST",
            f"https://email.{region}.amazonaws.com{SES_PATH}",
            "--header",
            "Content-Type: application/json",
        ]
        if session_token:
            command.extend(["--header", f"X-Amz-Security-Token: {session_token}"])
        command.extend(["--data-binary", payload.decode("utf-8")])
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    finally:
        credentials_file.close()
        try:
            Path(credentials_file.name).unlink()
        except FileNotFoundError:
            pass
    if result.returncode:
        detail = "\n".join(
            part for part in (result.stderr.strip(), result.stdout.strip()) if part
        )
        if not detail:
            detail = "No response returned."
        raise RuntimeError(f"Amazon SES rejected the test email: {detail}")

    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Amazon SES returned an unexpected response.") from error
    return response.get("MessageId", "(no message ID returned)")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_file", help="HTML campaign file to send")
    parser.add_argument("--group", choices=("personal", "team"), default="personal")
    parser.add_argument("--subject", help="Optional test-email subject line")
    parser.add_argument(
        "--message",
        help="Optional reviewer note displayed above the HTML for team sends",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    try:
        load_local_environment(ENV_FILE)
        campaign_file = resolve_campaign_file(args.html_file)
        sender = required_environment("SES_TEST_FROM_EMAIL")
        if not EMAIL_PATTERN.fullmatch(sender):
            raise ValueError("SES_TEST_FROM_EMAIL must be a valid email address.")
        recipients = recipients_for_group(args.group)
        html = campaign_file.read_text(encoding="utf-8")
        is_team_send = args.group == "team"
        team_message = (args.message or "") if is_team_send else ""
        message_id = send_with_ses(
            raw_email(
                html,
                sender,
                sender_name(),
                reply_to_address(),
                recipients,
                subject_for_file(campaign_file, args.subject),
                campaign_file,
                team_message,
                is_team_send,
            ),
            sender,
            recipients,
        )
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Email test not sent: {error}", file=sys.stderr)
        return 1

    print(
        f"Test email sent to {len(recipients)} recipient(s). SES MessageId: {message_id}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

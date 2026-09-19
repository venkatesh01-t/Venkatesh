import re
import socket
import logging

logger = logging.getLogger(__name__)

# RFC 5322 compliant regex with strict TLD validation
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$"
)

# Comprehensive blacklist of disposable / temporary / throwaway email domains
DISPOSABLE_EMAIL_DOMAINS = {
    "10minutemail.com", "10minutemail.net", "10minmail.com", "tempmail.com",
    "temp-mail.org", "temp-mail.io", "guerrillamail.com", "guerrillamail.net",
    "guerrillamail.org", "guerrillamailblock.com", "sharklasers.com", "grr.la",
    "mailinator.com", "mailinator.net", "mailinater.com", "yopmail.com",
    "yopmail.fr", "yopmail.net", "trashmail.com", "trashmail.net", "trashmail.org",
    "throwawaymail.com", "dispostable.com", "getairmail.com", "fakeinbox.com",
    "fakemailgenerator.com", "burnermail.io", "mohmal.com", "mytemp.email",
    "generator.email", "crazymailing.com", "dropmail.me", "inboxbear.com",
    "inboxkitten.com", "mailcatch.com", "mailnesia.com", "mintemail.com",
    "spambox.us", "tempr.email", "wegwerfmail.de", "zillamail.com",
    "emailondeck.com", "tempmailaddress.com", "fakemail.net", "armyspy.com",
    "cuvox.de", "dayrep.com", "einrot.com", "fleckens.hu", "gustr.com",
    "jourrapide.com", "rhyta.com", "superrito.com", "teleworm.us",
    "binkmail.com", "bobmail.info", "chacuo.net", "devnullmail.com",
    "discard.email", "disposablemail.com", "harakirimail.com", "maildrop.cc",
    "mailsac.com", "mytempmail.com", "nomail.xl.cx", "nowmymail.com",
    "spamgourmet.com", "spaml.de", "trashymail.com", "zoemail.org"
}

# Common automated spam bot keyword patterns
SPAM_KEYWORD_PATTERNS = [
    r"\bcrypto\s+investment\b",
    r"\bbitcoin\s+doubler\b",
    r"\bcasino\s+(bonus|slots)\b",
    r"\bviagra\b|\bcialis\b",
    r"\btelegram\s+(channel|group)\s+pump\b",
    r"\bseo\s+ranking\s+guarantee\b",
    r"\bearn\s+\$\d+[\d,]*\s+(daily|weekly|per\s+day)\b",
    r"\bpassive\s+income\s+guaranteed\b",
    r"\bwhatsapp\s+blaster\b"
]
SPAM_REGEX = re.compile("|".join(SPAM_KEYWORD_PATTERNS), re.IGNORECASE)


def validate_email_address(email: str) -> tuple[bool, str]:
    """
    Performs multi-stage email validation:
    1. Syntax & structure check (RFC 5322 regex, consecutive dots, length)
    2. Disposable / burner domain check
    3. Live DNS domain deliverability check (socket resolution with timeout)
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    email = (email or "").strip().lower()

    if not email:
        return False, "Email address is required."

    if len(email) > 254:
        return False, "Email address is too long (maximum 254 characters)."

    # Basic RFC syntax check
    if not EMAIL_REGEX.match(email):
        return False, "Please enter a valid email address format (e.g. name@domain.com)."

    # Reject consecutive dots or invalid leading/trailing characters
    if ".." in email:
        return False, "Email address cannot contain consecutive periods."

    parts = email.split("@")
    if len(parts) != 2:
        return False, "Invalid email address format."

    local_part, domain = parts
    if len(local_part) > 64:
        return False, "The username portion of the email cannot exceed 64 characters."

    # Disposable / Temporary burner email check
    if domain in DISPOSABLE_EMAIL_DOMAINS:
        return False, "Temporary or disposable email addresses are not accepted. Please provide your real email."

    # Live DNS host resolution check
    # Verifies that the domain actually has active network infrastructure to receive email
    try:
        # 1.5s timeout prevents blocking
        orig_timeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(1.5)
        try:
            socket.gethostbyname(domain)
        finally:
            socket.setdefaulttimeout(orig_timeout)
    except socket.gaierror:
        return False, f"The domain '{domain}' does not exist or has no active mail server. Please check for typos."
    except Exception as e:
        # Non-fatal timeout or network glitch fallback - allow if syntax is valid
        logger.warning(f"DNS check warning for {domain}: {e}")

    return True, ""


def check_spam_signals(payload: dict) -> tuple[bool, str]:
    """
    Inspects submission payload for spam indicators:
    1. Invisible honeypot field filled by bots
    2. Excessive URL link density
    3. Automated spam keyword matches
    
    Returns:
        (is_spam: bool, reason: str)
    """
    # 1. Invisible Honeypot Trap
    honeypot = payload.get("website_hp", "").strip()
    if honeypot:
        logger.warning(f"Honeypot trap triggered with value: '{honeypot}'")
        return True, "Bot activity detected."

    message = payload.get("message", "").strip()
    subject = payload.get("subject", "").strip()
    combined_text = f"{subject} {message}"

    # 2. Link density: Reject messages with more than 3 URLs
    urls = re.findall(r"https?://\S+|www\.\S+", combined_text, re.IGNORECASE)
    if len(urls) > 3:
        logger.warning(f"Spam rejected: excessive URLs ({len(urls)} found).")
        return True, "Your message contains too many website links. Please limit to at most 3."

    # 3. Known promotional spam phrases
    if SPAM_REGEX.search(combined_text):
        logger.warning(f"Spam rejected: matched spam keyword pattern in '{subject}'.")
        return True, "Your message was flagged by our automated spam filter."

    return False, ""

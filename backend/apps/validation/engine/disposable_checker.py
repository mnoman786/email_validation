import logging
from typing import Set
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY = 'disposable_domains_set'
CACHE_TTL = 3600

# Built-in known disposable domains.
# Keep this list large so detection works even before the DB is seeded.
BUILTIN_DISPOSABLE_DOMAINS: Set[str] = {
    # --- Guerrilla Mail family ---
    'guerrillamail.com', 'guerrillamail.net', 'guerrillamail.org',
    'guerrillamail.biz', 'guerrillamail.de', 'guerrillamail.info',
    'guerrillamailblock.com', 'grr.la', 'sharklasers.com', 'spam4.me',
    # --- Temp-Mail.org (most popular service, many domains) ---
    'temp-mail.org', 'temp-mail.io', 'temp-mail.de', 'temp-mail.ru',
    'temp-mail.live', 'temp-mail.app', 'temp-mail.email', 'temp-mail.to',
    'temp-mail.us', 'temp-mail.com',
    # Domains assigned by temp-mail.org / fakemailgenerator.com:
    'einrot.com', 'rhyta.com', 'cuvox.de', 'dayrep.com', 'fleckens.hu',
    'gustr.com', 'jourrapide.com', 'superrito.com', 'teleworm.us',
    'armyspy.com', 'chacuo.net', 'discard.email', 'spamgourmet.com',
    'spamgourmet.net', 'spamgourmet.org',
    # --- Mailinator ---
    'mailinator.com', 'mailinator2.com', 'mailinator0.com',
    'notmailinator.com', 'maildrop.cc', 'inoutmail.eu', 'inoutmail.de',
    'inoutmail.info', 'inoutmail.net',
    # --- 10 Minute Mail ---
    '10minutemail.com', '10minutemail.net', '10minutemail.org',
    '10minutemail.de', '10minutemail.ru', '10minutemail.be',
    '10minutemail.co.za', '10minutemail.info', '10minutemail.io',
    '10minutemail.us', '10minutemail.ml', '10minutemail.cf',
    '10minutemail.ga', '10minutemail.gq', '10minutemail.tk',
    'minutemail.com', 'minuteinbox.com', 'minsmail.com',
    # --- 20 minute mail ---
    '20minutemail.com', '20minutemail.net', '20minutemail.org',
    '20minutemail.it',
    # --- Yopmail ---
    'yopmail.com', 'yopmail.fr', 'cool.fr.nf', 'jetable.fr.nf',
    'nospam.ze.tc', 'nomail.xl.cx', 'mega.zik.dj', 'speed.1s.fr',
    'courriel.fr.nf', 'moncourrier.fr.nf', 'monemail.fr.nf',
    'monmail.fr.nf',
    # --- Trashmail ---
    'trashmail.com', 'trashmail.me', 'trashmail.net', 'trashmail.org',
    'trashmail.at', 'trashmail.io', 'trashmail.xyz', 'trashmail.app',
    'trashmail.fr', 'trashmail.global', 'trashmail.host',
    'trashmail.info', 'trashmail.is', 'trashmail.live', 'trashmail.top',
    # --- Throwaway / throwam ---
    'throwaway.email', 'throwam.com', 'throwam.net',
    'throwmail.de', 'throwmail.org', 'throwmail.net',
    # --- Dispostable / discard ---
    'dispostable.com', 'discardmail.com', 'discardmail.de',
    'discardmail.info', 'discardmail.net', 'discardmail.org',
    # --- Fake inbox ---
    'fakeinbox.com', 'fakemail.fr', 'fakemail.net',
    'fakeemailaddress.com', 'fakemailgenerator.com', 'fake-box.com',
    # --- Spam* ---
    'spam.la', 'spamavert.com', 'spambob.com', 'spambob.net',
    'spambob.org', 'spambog.com', 'spambog.de', 'spambog.ru',
    'spamcorpse.com', 'spamfree24.org', 'spamfree24.de', 'spamfree24.eu',
    'spamkill.info', 'spamspot.com', 'spamthis.co.uk', 'spamtrail.com',
    'spamhereplease.com', 'spamgoblin.com', 'spamgoblin.net',
    'spamfree.eu', 'spammy.host', 'spamex.com',
    # --- Temp / Temporary ---
    'tempmail.com', 'tempmail.net', 'tempmail.de', 'tempmail.ninja',
    'tempmail.plus', 'tempmail.zone', 'tempmail.gg', 'tempmail.lol',
    'tempemail.com', 'tempemail.net',
    'tempinbox.com', 'tempinbox.co.uk',
    'tempomail.fr', 'temporarioemail.com.br',
    'temporaryemail.net', 'temporaryemail.us',
    'temporaryforwarding.com', 'temporaryinbox.com',
    'tempr.email', 'temp.email', 'tempsky.com', 'tempsend.com',
    'tmpmail.org', 'tmpmail.net', 'tempmailaddress.com',
    'emailtemporar.ro', 'emailtemporaryfree.com',
    'gettempemail.com', 'get-temp-mail.com', 'temp-email.org',
    'temp-inbox.com', 'tempail.com',
    # --- Mail temp / mailtemp ---
    'mailtemp.info', 'mailtemp.net', 'mail-temp.com', 'mailtmp.com',
    'mail-easy.fr', 'mail-temporaire.fr',
    # --- Getnada ---
    'getnada.com', 'nada.email', 'nada.ltd',
    # --- Burner / inbox services ---
    'burnermail.io', 'inboxbear.com', 'inbox.si', 'inboxalias.com',
    'inbox2.info', 'inboxclean.org', 'inboxclean.com',
    'inboxkitten.com', 'emailondeck.com',
    # --- 33mail ---
    '33mail.com',
    # --- Mohmal ---
    'mohmal.com', 'mohmal.im', 'mohmal.net', 'mohmal.tech',
    # --- Mailnull ---
    'mailnull.com', 'devnullmail.com', 'mailnesia.com',
    'mailseal.de', 'mailwire.com', 'mailcatch.com',
    'mailboxy.fun', 'maildax.me',
    # --- GmailNator ---
    'gmailnator.com',
    # --- Spikes Email ---
    'spikes.email',
    # --- Wegwerfmail (German) ---
    'wegwerfmail.de', 'wegwerfmail.net', 'wegwerfmail.org',
    'zehnminuten.de', 'zehnminutenmail.de', 'nurfuerspam.de',
    'twinmail.de', 'maildu.de', 'mailde.de', 'mailde.info',
    # --- Misc well-known ---
    'getairmail.com', 'filzmail.com', 'mailexpire.com',
    'binkmail.com', 'bobmail.info', 'chammy.info', 'get2mail.fr',
    'jetable.net', 'jetable.org', 'jetable.pro',
    'lazyinbox.com', 'mailnew.com', 'mailscrap.com',
    'mailsiphon.com', 'mailslite.com', 'mailzilla.com', 'mailzilla.org',
    'meltmail.com', 'momentics.ru', 'mt2009.com', 'mt2014.com',
    'mt2015.com', 'mt2016.com',
    'netmails.com', 'netmails.net', 'nobulk.com', 'nomail.pw',
    'nospamfor.us', 'nospamthanks.info', 'nowmymail.com',
    'recode.me', 'recursor.net', 'regbypass.com',
    'safetymail.info', 'safetypost.de', 'sendspamhere.com',
    'shiftmail.com', 'shortmail.net', 'sibmail.com',
    'sneakemail.com', 'snkmail.com', 'sofimail.com',
    'sogetthis.com', 'soodonims.com', 'soodo.com',
    'trbvm.com', 'turual.com', 'tyldd.com', 'uggsrock.com', 'uroid.com',
    'wetrainbayarea.com', 'wetrainbayarea.org',
    'wilemail.com', 'willselfdestruct.com', 'winemaven.info',
    'wronghead.com', 'wuzupmail.net',
    'xagloo.com', 'xemaps.com', 'xents.com', 'xmaily.com', 'xoxy.net',
    'xyzfree.net', 'yuurok.com', 'z1p.biz', 'zehnminuten.de',
    'zippymail.info', 'zoemail.net', 'zoemail.org',
    'objectmail.com', 'obobbo.com', 'odnorazovoe.ru', 'oneoffemail.com',
    'pjjkp.com', 'plexolan.de', 'poofy.org', 'pookmail.com',
    'putthisinyourspamdatabase.com', 'antichef.com', 'antichef.net',
    'antireg.com', 'antireg.ru', 'antispam.de', 'antispam24.de',
    'antispammail.de', 'baxomale.ht.cx', 'beefmilk.com',
    'cryptmail.net', 'cryptmail.org',
    'disign-group.eu', 'disign-concept.eu',
    'mailorg.org', 'crazymailing.com', 'crazymailing.org',
    'fakesmtp.com',
    # --- Cock.li aliases (widely abused) ---
    'airmail.cc', 'cock.email', 'cock.li', 'waifu.club', 'tfwno.gf',
    'reddithub.com', 'notudork.com', 'horsefucker.org',
    'dicksinhisan.us', 'die-antwoord.eu',
}


def get_disposable_domains() -> Set[str]:
    """Get disposable domain set from cache or DB."""
    cached = cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    try:
        from apps.validation.models import DisposableDomain
        db_domains = set(DisposableDomain.objects.filter(is_active=True).values_list('domain', flat=True))
        all_domains = BUILTIN_DISPOSABLE_DOMAINS | db_domains
        cache.set(CACHE_KEY, all_domains, CACHE_TTL)
        return all_domains
    except Exception:
        return BUILTIN_DISPOSABLE_DOMAINS


def is_disposable_domain(domain: str) -> bool:
    """Check if domain is a known disposable email domain."""
    return domain.lower() in get_disposable_domains()


def invalidate_disposable_cache():
    """Invalidate the disposable domains cache."""
    cache.delete(CACHE_KEY)

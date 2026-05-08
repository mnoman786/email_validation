"""
Management command: update_disposable_domains

Fetches the community-maintained disposable email blocklist from GitHub
(~6,000+ domains) and loads them into the DisposableDomain model.

Usage:
    python manage.py update_disposable_domains
    python manage.py update_disposable_domains --source local
"""
import urllib.request
import logging
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

BLOCKLIST_URL = (
    "https://raw.githubusercontent.com/"
    "disposable-email-domains/disposable-email-domains/"
    "master/disposable_email_blocklist.conf"
)

# Fallback list of ~400 common disposable domains (used when GitHub is unreachable)
FALLBACK_DOMAINS = [
    # --- Guerrilla Mail family ---
    "guerrillamail.com","guerrillamail.net","guerrillamail.org","guerrillamail.biz",
    "guerrillamail.de","guerrillamail.info","grr.la","sharklasers.com",
    "guerrillamailblock.com","spam4.me",
    # --- Temp-Mail.org domains ---
    "temp-mail.org","einrot.com","rhyta.com","cuvox.de","dayrep.com",
    "fleckens.hu","gustr.com","jourrapide.com","superrito.com","teleworm.us",
    "armyspy.com","cuvox.de","dayrep.com","einrot.com","fleckens.hu",
    "gustr.com","jourrapide.com","rhyta.com","superrito.com","teleworm.us",
    # --- Mailinator family ---
    "mailinator.com","mailinator2.com","mailinator0.com","maildrop.cc",
    "inoutmail.eu","inoutmail.de","inoutmail.info","inoutmail.net",
    "discard.email","spamgourmet.com","spamgourmet.net","spamgourmet.org",
    # --- 10 Minute Mail ---
    "10minutemail.com","10minutemail.net","10minutemail.org","10minutemail.de",
    "10minutemail.ru","10minutemail.be","10minutemail.co.za","10minutemail.info",
    "10minutemail.io","10minutemail.us","10minutemail.ml","10minutemail.cf",
    "10minutemail.ga","10minutemail.gq","10minutemail.tk","minutemail.com",
    # --- Yopmail ---
    "yopmail.com","yopmail.fr","cool.fr.nf","jetable.fr.nf","nospam.ze.tc",
    "nomail.xl.cx","mega.zik.dj","speed.1s.fr","courriel.fr.nf",
    "moncourrier.fr.nf","monemail.fr.nf","monmail.fr.nf",
    # --- Trashmail ---
    "trashmail.com","trashmail.me","trashmail.net","trashmail.org",
    "trashmail.at","trashmail.io","trashmail.xyz","trashmail.app",
    # --- Throwaway / One-time ---
    "throwam.com","throwam.net","throwaway.email","throwam.net",
    "throwmail.de","throwmail.org","throwmail.net",
    "dispostable.com","discardmail.com","discardmail.de",
    "fakeinbox.com","fakemail.fr","fake-box.com","fakemailgenerator.com",
    # --- Spamex / Spam* ---
    "spamcorpse.com","spamfree24.org","spamfree24.de","spamfree24.eu",
    "spamkill.info","spamspot.com","spamthis.co.uk","spamtrail.com",
    "spam.la","spamavert.com","spambob.com","spambob.net","spambob.org",
    "spambog.com","spambog.de","spambog.ru","spamhereplease.com",
    # --- Temp / Temporary ---
    "tempmail.com","tempemail.com","tempemail.net","tempinbox.com",
    "tempinbox.co.uk","tempomail.fr","temporarioemail.com.br",
    "temporaryemail.net","temporaryemail.us","temporaryforwarding.com",
    "temporaryinbox.com","tempmail.net","tempmail.de","tempmail.ninja",
    "tempmail.plus","tempmail.zone","temp.email","temp.email","tempr.email",
    "tempsky.com","tempsend.com",
    # --- Mailnull / Misc null ---
    "mailnull.com","devnullmail.com","null.net","bitmail.com",
    # --- Wegwerfmail (German disposable) ---
    "wegwerfmail.de","wegwerfmail.net","wegwerfmail.org","zehnminuten.de",
    "zehnminutenmail.de","nurfuerspam.de","twinmail.de",
    # --- Misc well-known ---
    "getairmail.com","filzmail.com","mailexpire.com",
    "binkmail.com","bobmail.info","chammy.info","get2mail.fr",
    "jetable.net","jetable.org","jetable.pro","lazyinbox.com",
    "mailnew.com","mailscrap.com","mailsiphon.com","mailslite.com",
    "mailzilla.com","mailzilla.org","meltmail.com","momentics.ru",
    "mt2009.com","netmails.com","netmails.net","nobulk.com","nomail.pw",
    "nospamfor.us","nospamthanks.info","nowmymail.com",
    "recode.me","recursor.net","regbypass.com","safetymail.info",
    "safetypost.de","sendspamhere.com","shiftmail.com","shortmail.net",
    "sneakemail.com","snkmail.com","sofimail.com","sogetthis.com",
    "soodonims.com","trbvm.com","turual.com","tyldd.com","uggsrock.com",
    "uroid.com","wetrainbayarea.com","wetrainbayarea.org","wilemail.com",
    "willselfdestruct.com","winemaven.info","wronghead.com","wuzupmail.net",
    "xagloo.com","xemaps.com","xents.com","xmaily.com","xoxy.net",
    "xyzfree.net","yuurok.com","z1p.biz","za.com",
    "zippymail.info","zoemail.net","zoemail.org",
    # --- Mohmal / Arabic temp ---
    "mohmal.com","mohmal.im","mohmal.net","mohmal.tech",
    # --- Mailnesia / misc ---
    "mailnesia.com","mailnull.com","mailseal.de","mailtmp.com",
    "mailwire.com","mt2014.com","mt2015.com","mt2016.com",
    # --- GuerrillaMail aliases ---
    "antichef.com","antichef.net","antireg.com","antireg.ru",
    "antispam.de","antispam24.de","antispammail.de",
    "armyspy.com","baxomale.ht.cx","beefmilk.com",
    # --- Mailfort / Discard ---
    "discard.email","discardmail.de","discardmail.com",
    "discardmail.info","discardmail.net","discardmail.org",
    # --- Getnada ---
    "getnada.com","nada.email","nada.ltd",
    # --- Burner Mail ---
    "burnermail.io",
    # --- Protonmail-alike disposable ---
    "inboxbear.com",
    # --- Emailondeck ---
    "emailondeck.com",
    # --- Mailtemp ---
    "mailtemp.info","mailtemp.net","mail-temp.com",
    # --- Cock.li aliases (often abused) ---
    "airmail.cc","cock.email","cock.li","dicksinhisan.us","die-antwoord.eu",
    "horsefucker.org","notudork.com","prontomail.com","reddithub.com",
    "tfwno.gf","waifu.club",
    # --- YOPmail network ---
    "cool.fr.nf","jetable.fr.nf","nospam.ze.tc","nomail.xl.cx",
    "mega.zik.dj","speed.1s.fr","courriel.fr.nf","moncourrier.fr.nf",
    # --- Mailbox (temp services) ---
    "inboxbear.com","inbox.si","inboxalias.com","inbox2.info",
    # --- 33mail ---
    "33mail.com",
    # --- Anonaddy ---
    "anonaddy.com","anonaddy.me",
    # --- SimpleLogin ---
    "simplelogin.co","simplelogin.fr",
    # --- AnonAddy / Relay ---
    "relay.firefox.com",
    # --- Sharklasers / guerrilla ---
    "sharklasers.com","guerrillamailblock.com","grr.la",
    # --- TempMail.plus / newer services ---
    "tempmail.plus","tempmail.zone","tempmail.gg","tempmail.lol",
    "temp-mail.io","temp-mail.de","temp-mail.ru","temp-mail.live",
    "temp-mail.app","temp-mail.email","temp-mail.to","temp-mail.us",
    # --- Minuteinbox ---
    "minuteinbox.com","minsmail.com",
    # --- GmailNator ---
    "gmailnator.com",
    # --- ThrowAM ---
    "throwam.com","throwam.net",
    # --- Spikes Email ---
    "spikes.email",
    # --- Mailinator variants ---
    "notmailinator.com","mvrht.com","mvrht.net","mvrht.com",
    # --- Fake email ---
    "fakemail.net","fakeemailaddress.com","fakeemailgenerator.com",
    # --- random known ---
    "pukkum.com","pjjkp.com","plexolan.de","poofy.org","pookmail.com",
    "objectmail.com","obobbo.com","odnorazovoe.ru","oneoffemail.com",
    "sibmail.com","soodo.com","soodonims.com",
    "mailboxy.fun","maildax.me","mailcatch.com",
    # --- newer 2023-2025 services ---
    "tempmail.ninja","cryptmail.net","cryptmail.org",
    "inboxkitten.com","disign-group.eu","disign-concept.eu",
    "filzmail.com","mail-easy.fr","mail-temporaire.fr",
    "maildu.de","mailde.de","mailde.info","mailorg.org",
    "spamgoblin.com","spamgoblin.net","spamex.com",
    "fakesmtp.com","spamfree.eu","spammy.host",
    "trashmail.fr","trashmail.global","trashmail.host","trashmail.info",
    "trashmail.is","trashmail.live","trashmail.me","trashmail.top",
    "throwam.com","tempail.com","temp-inbox.com","temp-email.org",
    "tmpmail.org","tmpmail.net","tempmailaddress.com",
    "emailtemporar.ro","emailtemporaryfree.com",
    "gettempemail.com","get-temp-mail.com",
    "crazymailing.com","crazymailing.org",
    # --- Guerrilla originals ---
    "spam4.me","guerrillamail.biz",
    # --- 20minutemail ---
    "20minutemail.com","20minutemail.net","20minutemail.org","20minutemail.it",
    # --- mailnull variants ---
    "mailnull.com","devnullmail.com",
    # --- Inbox ---
    "inboxclean.org","inboxclean.com",
]


class Command(BaseCommand):
    help = "Fetches and imports the disposable email domain blocklist into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            choices=["github", "local"],
            default="github",
            help="Use 'github' to fetch from the community list, 'local' to use the fallback list only.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print how many domains would be added without saving.",
        )

    def handle(self, *args, **options):
        from apps.validation.models import DisposableDomain
        from apps.validation.engine.disposable_checker import invalidate_disposable_cache

        domains: set[str] = set()

        if options["source"] == "github":
            self.stdout.write("Fetching blocklist from GitHub …")
            try:
                req = urllib.request.Request(
                    BLOCKLIST_URL,
                    headers={"User-Agent": "EmailGuard/1.0"},
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    content = resp.read().decode("utf-8")
                for line in content.splitlines():
                    line = line.strip().lower()
                    if line and not line.startswith("#"):
                        domains.add(line)
                self.stdout.write(self.style.SUCCESS(f"Fetched {len(domains):,} domains from GitHub."))
            except Exception as exc:
                self.stdout.write(
                    self.style.WARNING(f"GitHub fetch failed ({exc}). Falling back to local list.")
                )
                domains.update(d.lower() for d in FALLBACK_DOMAINS)
        else:
            domains.update(d.lower() for d in FALLBACK_DOMAINS)
            self.stdout.write(f"Using local fallback list ({len(domains):,} domains).")

        if options["dry_run"]:
            self.stdout.write(f"[dry-run] Would import {len(domains):,} domains.")
            return

        existing = set(
            DisposableDomain.objects.filter(domain__in=domains).values_list("domain", flat=True)
        )
        new_domains = domains - existing
        if not new_domains:
            self.stdout.write("All domains already exist in the database.")
        else:
            objs = [DisposableDomain(domain=d, source="community", is_active=True) for d in new_domains]
            DisposableDomain.objects.bulk_create(objs, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS(f"Added {len(new_domains):,} new disposable domains."))

        invalidate_disposable_cache()
        total = DisposableDomain.objects.filter(is_active=True).count()
        self.stdout.write(self.style.SUCCESS(f"Done. Total disposable domains in DB: {total:,}"))

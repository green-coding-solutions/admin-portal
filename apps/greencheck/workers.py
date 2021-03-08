from dataclasses import dataclass
from django.utils import dateparse
from apps.greencheck.models import Greencheck, GreenDomain
from apps.accounts.models import Hostingprovider

import tld
import ipaddress
import logging

console = logging.StreamHandler()
logger = logging.getLogger(__name__)
# logger.setLevel(logging.WARN)
# logger.addHandler(console)


@dataclass
class SiteCheck:
    """
    A representation of the Sitecheck object from the PHP app.
    We use it as a basis for logging to the Greencheck, but also maintaining
    our green_domains tables.
    """

    url: str
    ip: str
    data: bool
    green: bool
    hosting_provider_id: int
    checked_at: str
    match_type: str
    match_ip_range: int
    cached: bool


class SiteCheckLogger:
    """
    A worker to consume messages from RabbitMQ, generated by the
    dramatiq library in this application
    """

    def log_sitecheck_to_database(self, sitecheck: SiteCheck):
        """
        Accept a sitecheck and log to the greencheck logging table,
        along with the green domains table (green_presenting).

        """
        logger.debug(sitecheck)

        try:
            hosting_provider = Hostingprovider.objects.get(
                pk=sitecheck.hosting_provider_id
            )
        except Hostingprovider.DoesNotExist:
            # if we have no hosting provider we leave it out
            hosting_provider = None

        if sitecheck.green and hosting_provider:
            self.update_green_domain_caches(sitecheck, hosting_provider)

        try:
            fixed_tld, *_ = (tld.get_tld(sitecheck.url, fix_protocol=True),)
        except tld.exceptions.TldDomainNotFound:

            try:
                ipaddress.ip_address(sitecheck.url)
                fixed_tld = ""
            except Exception:
                logger.exception(
                    "not a domain, or an IP address, not logging. Sitecheck results: {sitecheck}"
                )
                return {"status": "Error", "sitecheck": sitecheck}

        except Exception:
            logger.exception(
                "Unexpected error. Not logging the result. Sitecheck results: {sitecheck}"
            )
            return {"status": "Error", "sitecheck": sitecheck}

        # finally write to the greencheck table

        if hosting_provider:
            res = Greencheck.objects.create(
                hostingprovider=hosting_provider.id,
                greencheck_ip=sitecheck.match_ip_range,
                date=dateparse.parse_datetime(sitecheck.checked_at),
                green="yes",
                ip=sitecheck.ip,
                tld=fixed_tld,
                type=sitecheck.match_type,
                url=sitecheck.url,
            )
            logger.debug(f"Greencheck logged: {res}")
        else:

            res = Greencheck.objects.create(
                date=dateparse.parse_datetime(sitecheck.checked_at),
                green="no",
                ip=sitecheck.ip,
                tld=fixed_tld,
                url=sitecheck.url,
            )
            logger.debug(f"Greencheck logged: {res}")

        # return result so we can inspect if need be
        return {"status": "OK", "sitecheck": sitecheck, "res": res}

    def update_green_domain_caches(
        self, sitecheck: SiteCheck, hosting_provider: Hostingprovider
    ):
        """
        Update the caches - namely the green domains table, and if running Redis
        """

        try:
            green_domain = GreenDomain.objects.get(url=sitecheck.url)
        except GreenDomain.DoesNotExist:
            green_domain = GreenDomain(url=sitecheck.url)

        green_domain.hosted_by = hosting_provider.name
        green_domain.hosted_by_id = sitecheck.hosting_provider_id
        green_domain.hosted_by_website = hosting_provider.website
        green_domain.partner = hosting_provider.partner
        green_domain.modified = sitecheck.checked_at
        green_domain.green = sitecheck.green
        green_domain.save()

    def update_redis_domain_cache(self, green_domain: GreenDomain):
        """
        Accept a GreenDomain object, and write it to the corresponding
        redis cache keys
        """
        # TODO: this is primarily used for logger processes
        # write it to the domains namespace

        # write it to the recent domains collection

        pass
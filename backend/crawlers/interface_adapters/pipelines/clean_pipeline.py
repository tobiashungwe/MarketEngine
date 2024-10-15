import re
from scrapy.exceptions import DropItem

class CleanCompanyDataPipeline:
    def process_item(self, item, spider):
        # Clean and validate name
        if 'name' in item:
            item['name'] = item['name'].strip()
        else:
            raise DropItem("Missing company name")

        # Clean and validate email
        if 'email' in item and item['email']:
            item['email'] = item['email'].strip().lower()
            if not re.match(r"[^@]+@[^@]+\.[^@]+", item['email']):
                raise DropItem(f"Invalid email: {item['email']}")
        else:
            item['email'] = None  # Optionally handle missing emails

        # Clean address
        if 'address' in item:
            item['address'] = item['address'].strip()

        # Clean industry
        if 'industry' in item:
            item['industry'] = item['industry'].strip()

        return item
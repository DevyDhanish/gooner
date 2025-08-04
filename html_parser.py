from bs4 import BeautifulSoup

class HtmlParser:
    def __init__(self, html_body: str):
        self.soup = BeautifulSoup(html_body, "html.parser")

    def get_by_id(self, element_id: str):
        return self.soup.find(id=element_id)

    def get_by_class(self, class_name: str):
        return self.soup.find_all(class_=class_name)

    def get_by_tag(self, tag_name: str):
        return self.soup.find_all(tag_name)

    def get_attr(self, element, attr_name: str):
        return element.get(attr_name)

    def get_text(self, element=None):
        if element:
            return element.get_text()
        return self.soup.get_text()

    def get_data_csrf_token(self, token_id: str = "token_full"):
        el = self.get_by_id(token_id)
        if el:
            return el.get("data-csrf-token")
        return None

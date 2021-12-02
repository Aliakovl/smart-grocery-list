from bs4 import BeautifulSoup
import requests
import re


class ParserRecipe:
    def __init__(self, url):
        self.url = url

    def parse(self):

        if self.url.startswith('https://m.povar.ru'):
            self.url = 'https://povar.ru' + self.url[18:]

        print(self.url)

        page = requests.get(self.url)

        # get page of the user's recepy
        soup = BeautifulSoup(page.text, "html.parser")

        # find href for printing
        allIngr = soup.find('a', class_='actionsNewPrint')
        url = 'https://povar.ru' + allIngr.attrs['href']
        page = requests.get(url)

        self.name = soup.find('h1', class_='detailed').text

        self.soup = BeautifulSoup(page.text, "html.parser")

    def get_soup(self):
        return self.soup

    def recipe(self):
        recipies = self.soup.findAll('div', class_='recept_column')

        recipe = []
        for data in recipies:
            if data.find('li') is not None:
                recipe.append(data.text)
        return recipe[0]

    def ingred_units(self):
        # print ingredients and units
        allIngr = self.soup.findAll('div', class_='ingredients')
        ingrs = []
        ingrs_size = []
        for data in allIngr[0].findAll('p'):
            ingr = ''
            ingr_size = ''
            found = False
            for i in data.text:
                if i == '\n':
                    ingr_size = ingr_size + '\n'
                    found = False
                if found:
                    ingr_size = ingr_size + i
                if not i == '—' and not found:
                    ingr = ingr + i
                else:
                    found = True
            ingrs.append(ingr.replace(u'\xa0', u'').strip().lower())
            ingrs_size.append(ingr_size.replace(u'\xa0', u''))
        return ingrs, ingrs_size

    def pipe(self):
        self.parse()
        ingrs, ingrs_size = self.ingred_units()
        reg = r'^\D*((\d+\.?\d*)|(\d+\-\d+)).*'
        nums = []
        for a in ingrs_size:
            line = re.sub(reg, r'\1', a, flags=re.X)
            ns = [float(j) for j in line.split('-')]
            av = sum(ns) / len(ns)
            nums.append(av)
        return list(zip(ingrs, nums, ingrs_size))

    def get_name(self):
        return self.name


# recipe
# parser = ParserRecipe('https://povar.ru/recipes/sup_harcho_iz_baraniny_klassicheskii-57059.html')
# print(parser.pipe())

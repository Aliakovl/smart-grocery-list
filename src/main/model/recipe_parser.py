from bs4 import BeautifulSoup
import requests
import re


class ParserRecipe:
    def __init__(self, url):
        self.url = url

    def parse(self):
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
        def arr_of_tuples_of_ingrs(nums, ingrs_size):
            new_list = []
            for i in nums:
                new_num = ''
                if len(i) > 0:
                    if len(i) == 1 and i[0] == ',':
                        continue
                    for j in i:
                        new_num += j
                else:
                    continue
                new_list.append(new_num)

            for i in range(len(new_list)):
                ingrs_size[i] = ingrs_size[i].replace(new_list[i], '')
                new_list[i] = float(new_list[i].replace(',', '.'))

            return list(zip(ingrs, new_list, ingrs_size))
        self.parse()
        ingrs, ingrs_size = self.ingred_units()
        print(ingrs)
        legal_chars = r'[0-9_,]'
        nums = []
        for i in ingrs_size:
            n = [re.findall(legal_chars, x) for x in i.split()]
            nums.append(n[0])
        arr_of_tuples = arr_of_tuples_of_ingrs(nums, ingrs_size)
        return arr_of_tuples

    def get_name(self):
        return self.name


# recipe
# parser = ParserRecipe('https://povar.ru/recipes/sup_harcho_iz_baraniny_klassicheskii-57059.html')
# print(parser.pipe())

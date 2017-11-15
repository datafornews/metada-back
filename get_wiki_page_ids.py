# To be run within the pm shell

from app.graph_models import *
import wikipedia

def get_ids():
    errors = {'20 Minutes',
              'Aisne Nouvelle',
              'Arnaud Lagardère',
              'Artémis',
              'Bolloré',
              'Chérie 25',
              'Chérie FM',
              'Crédit Agricole',
              'Crédit Mutuel',
              'DNA',
              'Edouard Condurier',
              'Famille Hutin',
              'France Ô',
              'François Pinault',
              'Groupe Figaro',
              "Groupe l'Agefi",
              'Gérard Lignac',
              'Jean-Sébastien Ferjou',
              "L'Alsace",
              "L'Ardennais",
              "L'Est Républicain",
              "L'Est-Éclair",
              "L'Express",
              "L'Indépendant",
              "L'Obs",
              "L'Opinion",
              "L'Union",
              "L'Yonne Républicaine",
              "L'Écho Républicain",
              "L'Éclair",
              'LCP Assemblée Nationale',
              'LNEI',
              'La Dépêche Du Midi',
              'La Nouvelle République Des Pyrénées',
              'La République Des Pyrénées',
              'La République Du Centre',
              'Lampsane ISA',
              'Le Berry Républicain',
              "Le Courrier De L'Ouest",
              "Le Journal D'Elbeuf",
              'Le Progrès',
              'Le Progrès De Fecamp',
              'Le Républicain Lorrain',
              'Le Télégramme',
              'Les Echos',
              'Les Echos Weekend',
              'Libération',
              'Libération Champagne',
              "Mouv'",
              'Nethys',
              'Nord Éclair',
              'Numéro 23',
              'Pierre Bergé',
              'Presse Océan',
              'Public Sénat',
              'République Française',
              'Vaucluse Matin',
              'Vincent Bolloré',
              'Xavier Ellie'}
    wikipedia.set_lang('fr')
    # errors = {}
    for e in Entity.query.all():
        if hasattr(e, 'wiki_page_id'):
            if e.wiki_page_id and e.wiki_page_id > 0:
                continue
        if e.name in errors:
            continue
        print('\n', e.name, '\n')
        if hasattr(e, 'wiki'):
            if len(e.wiki) > 0:
                wikiId = e.wiki.split('/')[-1]
                w = wikipedia.search(wikiId)
                if len(w) > 0:
                    w = wikipedia.page(w[0])
                else:
                    errors.add(e.name)
                    continue
                print(w.summary)
                save = input('\nSave id? -> yes (default), no, stop  :  ')
                if 'stop' in save:
                    break
                if 'n' in save:
                    if 'y' in input('Add to errors?'):
                        errors.add(e.name)
                    continue
                e.wiki_page_id = w.pageid
                db.session.commit()
        print(e.wiki_page_id, '\n')

if __name__ == '__main__':
    pass
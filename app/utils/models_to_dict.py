def clear_instance(model_instance):
    dic = model_instance.__dict__.copy()
    keys_to_delete = {
        '_sa_instance_state',
        'created_by_id',
        'created_at',
        'updated_by_id',
        'updated_at'
    }
    ks = set(dic.keys())
    for k in ks.intersection(keys_to_delete):
        del dic[k]
    return dic


def user_to_dict(user):
    dic = clear_instance(user)
    keys = {'username', 'first_name', 'last_name', 'id', 'email'}
    user_dic = {k: dic[k] for k in keys}
    user_dic['confirmed'] = user.confirmed_at is not None
    return user_dic


def entity_to_dict(en):
    dic = clear_instance(en)
    dic['category'] = dic['category'].code
    if dic['website']:
        dic['website'] = dic['website']
    if en.wiki:
        dic['wiki'] = wiki_data_to_dict(en.wiki)

    return dic


def wiki_data_to_dict(wd):
    return {
        'lang': wd.lang,
        'title': wd.title
    }


def edge_to_dict(ed):
    return clear_instance(ed)
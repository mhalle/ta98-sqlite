from bs4 import BeautifulSoup


def parse(fp_or_str):
    """parse TA98 english web pages into a Python dictionary"""

    soup = BeautifulSoup(fp_or_str, "html.parser")

    res = soup.find_all(class_=('SectionTitle', 'SectionContent'))
    sections = {}
    found_current_in_hierarchy = False
    ta_hierarchy = []
    for r in res:
        if 'SectionTitle' in r['class']:
            section_key = r.text.strip()
            section_val = sections[section_key.replace(' ', '_')] = {}
        else:  # SectionContent
            if section_key == 'FMA Taxonomy':
                parent = r.find(class_='ENb')
                parent_id_name = get_key_val(parent)
                if parent_id_name:
                    section_val['FMA_parent'] = parent_id_name
                specs = r.find_all(class_='spec')
                fma_ancestors = list(reversed([get_key_val(x) for x in specs]))
                section_val['FMA_ancestors'] = fma_ancestors
                section_val['FMA_name'] = fma_ancestors[0][1]
            elif section_key == 'TA98 Hierarchy':
                spec = r.find(class_='spec')
                ta_hierarchy.append(get_key_val_title(spec))
                current_entry = r.find(class_='LAa')
                if current_entry and not found_current_in_hierarchy:
                    found_current_in_hierarchy = True
                    parent = current_entry.find_previous(class_='LAb')
                    if parent:
                        section_val['TA98_parent'] = get_key_val_title(parent.parent)
            else:
                for rub in r.find_all(class_='rub'):
                    rubval = rub.text.strip().replace(' ', '_')
                    spec = rub.find_next_sibling(class_='spec')
                    specval = spec.text.strip()
                    if rubval in section_val:
                        curval = section_val[rubval]
                        if isinstance(curval, list):
                            curval.append(specval)
                        else:
                            section_val[rubval] = [curval, specval]
                    else:
                        section_val[rubval] = specval

    output = {'Properties': []}
    for prop_name, prop_val in sections.items():
        if prop_name == 'Properties':
            output['Properties'] = [x.replace(' ', '_') for x in list(prop_val.keys())]
        else:
            output.update(prop_val)
    ta_ancestors = []
    for i in ta_hierarchy:
        ta_ancestors.append(i)
        if i[0] == output['TA_code']:
            break

    output['TA98_ancestors'] = list(reversed(ta_ancestors))
    return output

def get_key_val(spec):
    '''extract key/value from a TA98 section'''
    spec_val = spec.text.strip()
    rub_val = spec.find_previous(class_='rub').text.strip()
    return [rub_val, spec_val]

def get_key_val_title(spec):
    '''extract key/value from a TA98 section. Similar to get_key_val,
    but use the title attribute.'''

    try:
        spec_val = spec['title'].strip()
    except KeyError:
        spec_val = spec.text.strip()

    rub_val = spec.find_previous(class_='rub').text.strip()
    return [rub_val, spec_val]

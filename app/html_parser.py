from bs4 import BeautifulSoup


def parse_qa_requirements(html_content):
    # Parse HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize result dictionary
    qa_requirements = {}

    # Find the QA Requirement table
    table = soup.find('table', id='sect_s3')
    if not table:
        print("Table with id='sect_s3' not found in HTML.")
        return qa_requirements

    # Iterate through each row in the table
    for row in table.find_all('tr', class_='formRow'):
        tds = row.find_all('td')
        i = 0
        while i < len(tds):
            td = tds[i]
            label_elem = td.find('label', class_='fieldLabel')
            if label_elem:
                label_text = label_elem.get_text(strip=True)
                if 'label' in td.get('class', []):  # Text field label
                    i += 1
                    if i < len(tds):
                        content_td = tds[i]
                        if 'cell' in content_td.get('class', []):
                            cell_text = content_td.get_text(strip=True).strip()
                            qa_requirements[label_text] = cell_text
                else:  # Checkbox field
                    checkmark = td.find('img', alt='Yes')
                    qa_requirements[label_text] = bool(checkmark)
            i += 1

    return qa_requirements
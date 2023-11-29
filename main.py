import base64
from fastapi import FastAPI, HTTPException
from azure.devops.v7_1.work_item_tracking.models import Wiql, JsonPatchOperation
from bs4 import BeautifulSoup
from azure_config import AzureConfig, get_azure_devops_connection, OpenIA
from openai import OpenAI

app = FastAPI(
    title="Automation IA Azure",
    description="Uma Inteligência no Azure Devops.",
    version="1.0",
)

@app.get("/workitems",
         tags=["Azure DevOps Automation"]
         )
def get_workitems():
    """
    Retrieve a list of User Stories from Azure DevOps

    Endpoint to fetch User Stories from Azure DevOps using the Azure DevOps REST API.

    Returns:

        List[Dict]: A list of dictionaries containing information about each User Story.

                    Each dictionary includes 'id', 'title', 'description', 'workItemType', 'acceptance_criteria'.
    """
    work_item_tracking_client = get_azure_devops_connection().clients.get_work_item_tracking_client()

    query = "SELECT * FROM workitems Where [System.WorkItemType] = 'User Story' "
    wiql = Wiql(query=query)
    query_results = work_item_tracking_client.query_by_wiql(wiql).work_items

    results = []
    for item in query_results:
        work_item = work_item_tracking_client.get_work_item(item.id)
        try:
            return_acceptance_criteria = work_item.fields.get('Microsoft.VSTS.Common.AcceptanceCriteria', '')
            acceptance_criteria = remover_caracteres_html(return_acceptance_criteria)
        except KeyError:
            acceptance_criteria = ""

        try:
            description = remover_caracteres_html(work_item.fields['System.Description'])
        except KeyError:
            description = ""

        result = {"id": work_item.id, 
                  "title": work_item.fields['System.Title'],
                  "description": description,
                  "workItemType": work_item.fields['System.WorkItemType'],
                  "acceptance_criteria": acceptance_criteria
                  }
        results.append(result)

    return results

@app.get("/user-story/{work_item_id}/description", 
         tags=["Azure DevOps Automation"]
         )
async def get_user_story_description(work_item_id: int):
    """
    Endpoint to retrieve the description of a specific User Story from Azure DevOps.

    Args:
        work_item_id (int): The unique identifier of the User Story.

    Returns:

        str: The HTML-free description text of the User Story.
        
    Raises:

        HTTPException: 
            - 404 Not Found if the User Story has no description.
            - 500 Internal Server Error for any other unexpected errors during the retrieval process.
    """
    try:
        wit_client = get_azure_devops_connection().clients.get_work_item_tracking_client()
        work_item = wit_client.get_work_item(work_item_id, project= AzureConfig.project_id)

        if work_item.fields['System.Description'] is None:
            raise HTTPException(status_code=404, detail="No Description write :( ")
        
        description = work_item.fields['System.Description']
        description_text = remover_caracteres_html(description)

        return description_text

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recovery WorkItems: {str(e)}")


@app.put("/user-story/{work_item_id}/update-criteria-customized", 
         tags=["Azure DevOps Automation"]
         )
async def update_criteria_accept(work_item_id: int, new_criteria_accept: str):
    
    try:
        wit_client = get_azure_devops_connection().clients.get_work_item_tracking_client()
        work_item = wit_client.get_work_item(work_item_id, project= AzureConfig.project_id)

        if work_item.fields['System.Description'] is None:
            raise HTTPException(status_code=404, detail="No Description write :( ")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recovery WorkItems: {str(e)}")

    acceptance_criteria = work_item.fields.get('Microsoft.VSTS.Common.AcceptanceCriteria')

    if acceptance_criteria is None or acceptance_criteria.strip() == '':
        patch_operation = JsonPatchOperation(
            op= "replace",
            path= f"/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
            value= new_criteria_accept
        )
        response = wit_client.update_work_item(
            document=[patch_operation],
            id=work_item.id
        )
        return (f"AcceptanceCriteria field successfully updated to: {new_criteria_accept}")
    else:
        return (f"Field already filled in. Field: {acceptance_criteria}")

@app.put("/user-story/{work_item_id}/update-criteria-id", 
         tags=["Azure DevOps Automation"]
         )
async def update_criteria_accept(work_item_id: int):
    
    try:
        wit_client = get_azure_devops_connection().clients.get_work_item_tracking_client()
        work_item = wit_client.get_work_item(work_item_id, project= AzureConfig.project_id)

        if work_item.fields['System.Description'] is None:
            raise HTTPException(status_code=404, detail="No Description write :( ")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error recovery WorkItems: {str(e)}")

    acceptance_criteria = work_item.fields.get('Microsoft.VSTS.Common.AcceptanceCriteria')

    if acceptance_criteria is None or acceptance_criteria.strip() == '':

        return_text = openIArefactory(work_item.fields['System.Description'])
        print(return_text)
        new_criteria_accept = formatar_texto_html(return_text)
        separador = "f'<div>\n\n----------------------------\n\n</div>'"
        texto_final = f"{return_text}{separador}{new_criteria_accept}"

        patch_operation = JsonPatchOperation(
            op= "replace",
            path= f"/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
            value= new_criteria_accept
        )
        response = wit_client.update_work_item(
            document=[patch_operation],
            id=work_item.id
        )
        return (f"AcceptanceCriteria field successfully updated to: {new_criteria_accept}")
    else:
        return (f"Field already filled in. Field: {acceptance_criteria}")


def remover_caracteres_html(texto_html):
    soup = BeautifulSoup(texto_html, "html.parser")
    texto_sem_html = soup.get_text(separator=" ", strip=True)

    # Remover aspas do início e do final, se presentes
    if texto_sem_html.startswith('"') and texto_sem_html.endswith('"'):
        texto_tratado = texto_sem_html[1:-1]
    else:
        texto_tratado = texto_sem_html

    return texto_tratado


def openIArefactory(description):

    client = OpenAI(api_key=OpenIA.api_key)
    
    EnsinaChat = "Criar com a mensagem a seguir, os 10 principais criterios de aceites para a solicitação a seguir:"
    mensagem = description
    
    completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": EnsinaChat},
        {"role": "user", "content": mensagem}
    ]
    )
    return completion.choices[0].message.content
'''
def formatar_texto_html(texto):
    numeros = [str(i) for i in range(1, 16)]

    for numero in numeros:
        separador = '.' if '.' in numero else '-' if '-' in numero else ''
        texto = texto.replace(f'{numero}{separador}', f'<div><b>{numero}{separador}</b>&nbsp;')

    texto_formatado = f'{texto}'

    return texto_formatado
'''
def formatar_texto(texto):
    # Substitui números e pontos por uma quebra de linha
    texto_formatado = texto.replace('1.', '\n1.').replace('2.', '\n2.').replace('3.', '\n3.').replace('4.', '\n4.')\
        .replace('5.', '\n5.').replace('6.', '\n6.').replace('7.', '\n7.').replace('8.', '\n8.').replace('9.', '\n9.')\
        .replace('10.', '\n10.').replace('11.', '\n11.').replace('12.', '\n12.').replace('13.', '\n13.')\
        .replace('14.', '\n14.').replace('15.', '\n15.')
    
    return texto_formatado
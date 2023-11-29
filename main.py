import base64
from fastapi import FastAPI, HTTPException
from azure.devops.v7_1.work_item_tracking.models import Wiql, JsonPatchOperation
from bs4 import BeautifulSoup
from azure_config import AzureConfig, get_azure_devops_connection

app = FastAPI(    
    title="Automation IA Azure",
    description="Uma Inteligência no Azure Devops.",
    version="1.0",
)

@app.get("/", 
         description="Esta rota retorna informações gerais.", 
         tags=["Azure DevOps Automation"]
         )
async def info_root():
    return {"message": "Acesse /docs para visualizar a documentação."}


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
            acceptance_criteria = "Campo não encontrado"

        result = {"id": work_item.id, 
                  "title": work_item.fields['System.Title'],
                  "description": remover_caracteres_html(work_item.fields['System.Description']),
                  "workItemType": work_item.fields['System.WorkItemType'],
                  "acceptance_criteria": remover_caracteres_html(acceptance_criteria)
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


@app.put("/user-story/{work_item_id}/update-criteria", 
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


    # Adicione a lógica para validar se "criteria_accept" está vazio e, se sim, atualize o campo
    if acceptance_criteria is None:
        # Crie uma operação de patch para atualizar o campo
        patch_operation = JsonPatchOperation(
            op= "replace",
            path= f"/fields/Microsoft.VSTS.Common.AcceptanceCriteria",
            value= new_criteria_accept
        )

        # Aplique a operação de patch ao item de trabalho existente
        response = wit_client.update_work_item(
            document=[patch_operation],
            id=work_item.id
        )
        print(response)

        if response.status_code == 200:
            return (f"Campo AcceptanceCriteria atualizado com sucesso para {new_criteria_accept}")
        else:
            return (f"Falha ao atualizar o campo AcceptanceCriteria. Código de status: {response.status_code} {response.text}")


def remover_caracteres_html(texto_html):
    soup = BeautifulSoup(texto_html, "html.parser")
    texto_sem_html = soup.get_text(separator=" ", strip=True)

    # Remover aspas do início e do final, se presentes
    if texto_sem_html.startswith('"') and texto_sem_html.endswith('"'):
        texto_tratado = texto_sem_html[1:-1]
    else:
        texto_tratado = texto_sem_html

    return texto_tratado
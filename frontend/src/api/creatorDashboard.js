const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000";

function authHeaders(){
  const accessToken =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    "";

  return accessToken
    ? { Authorization:`Bearer ${accessToken}` }
    : {};
}

async function request(path){
  const response=await fetch(
    `${API_BASE}${path}`,
    {
      headers:{
        "Content-Type":"application/json",
        ...authHeaders(),
      },
    }
  );

  const data=await response
    .json()
    .catch(()=>({}));

  if(!response.ok){
    throw new Error(
      data.detail ||
      data.error ||
      `Request failed: ${response.status}`
    );
  }

  return data;
}

export function getCreatorDashboard(userId){
  return request(
    `/platform/v15/dashboard/${userId}`
  );
}

export function getCreatorDashboardSummary(userId){
  return request(
    `/platform/v15/dashboard/${userId}/summary`
  );
}
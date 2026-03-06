export async function getDashboard(initData){

const response = await fetch("/api/dashboard",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body: JSON.stringify({
initData:initData
})

})

return await response.json()

}
import {useState} from "react"


export default function AddFriend(){
    const [user,setUser] = useState("")
    const [error,setError] = useState("")
    const [success,setSuccess] = useState("")
    const token = localStorage.getItem("token")
    async function sendFriendRequest(event){
        event.preventDefault()
        const url = "/api/friendrequest"
        const requestOptions = {
            method: 'POST',
            headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            body:JSON.stringify({"username":user})
            }
       const response = await fetch(url,requestOptions)
       const data = await response.json()
       if(response.status === 409){
            setSuccess("")
            setError(data.detail)
       }else{
            setError("")
            setSuccess("Friend request sent")
       }
       setUser("")
    }
    return(
        <div className="user-requests-container" onSubmit={sendFriendRequest}>
             <form>
                <input type="text" name="user" placeholder="You can add friends with their Discord username." value={user} onChange={(e) => setUser(e.target.value)} required/>
             </form>
             {error && (
                <p className="error">{error}</p>
             )}
             {success && (
                <p className="success">{success}</p>
             )}
        </div>
    )
}
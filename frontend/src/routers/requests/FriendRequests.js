import {useState,useEffect,useContext} from "react"
import {Context} from "../../Context.js"
import {useNavigate} from "react-router-dom"

export default function FriendRequests(){
    const [friendRequests,setFriendRequests] = useState([])
    const {getDms,username} = useContext(Context)
    const navigate = useNavigate()
    const token = localStorage.getItem("token")
    useEffect(() => {
        async function getFriendRequests(){
            const url = "/api/friendrequests"
            const requestOptions = {
                method: 'GET',
                headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token}
                }
            const response = await fetch(url,requestOptions)
            const data = await response.json()
            if(response.status === 401){
                navigate("/login")
            }else{
                setFriendRequests(data)
            }
        }
        getFriendRequests()
    },[])
    async function createDm(user){
        const url = "/api/dm"
        const requestOptions = {
            method: 'POST',
            headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            body:JSON.stringify({"username":user})
        }
        const response = await fetch(url,requestOptions)
        return response
    }
    async function deleteFriendRequest(user){
        const url = "/api/friendrequest"
        const requestOptions = {
            method: 'DELETE',
            headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            body:JSON.stringify({"username":user})
        }
        const response = await fetch(url,requestOptions)
        setFriendRequests(FriendRequests => (
            FriendRequests.filter(request => request.sender !== user)
        ))
    }
    async function acceptFriendRequest(user){
        const url = "/api/friend"
        const requestOptions = {
            method: 'POST',
            headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            body:JSON.stringify({"username":user})
        }
        const response = await fetch(url,requestOptions)
        setFriendRequests(FriendRequests => (
            FriendRequests.filter(request => request.sender !== user)
        ))
        const createDmResponse = await createDm(user)
        if(createDmResponse.status !== 409){
            getDms()
        }
    }
    return(
        <div className="user-requests-container" id="pending-container">
            <form onSubmit={(e) => e.preventDefault()}>
                <input type="text" name="user" placeholder="Search" />
            </form>
            <p className="count">PENDING - <span>{friendRequests.length}</span></p>
            <div className="pending-requests">
                {friendRequests && friendRequests.length > 0 && (
                    friendRequests.map(request => {
                        if(request.sender == username){
                            return(
                                <div className="request">
                                    <img src={request.receiverprofile}/>
                                    <div>
                                        <p>{request.receiver}</p>
                                        <span>Outgoing Friend Request</span>
                                    </div>
                                    <div className="request-icons">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-x cancel" onClick={() => deleteFriendRequest(request.receiver)}><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                                    </div>
                                 </div>
                            )
                        }
                        if(request.receiver == username){
                            return(
                                <div className="request">
                                    <img src={request.senderprofile}/>
                                    <div>
                                        <p>{request.sender}</p>
                                        <span>Incoming Friend Request</span>
                                    </div>
                                    <div className="request-icons">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-check check" onClick={() => acceptFriendRequest(request.sender)}><polyline points="20 6 9 17 4 12"></polyline></svg>
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" className="feather feather-x decline" onClick={() => deleteFriendRequest(request.sender)}><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                                    </div>
                                 </div>
                            )
                        }

                }))}
            </div>
       </div>
    )
}
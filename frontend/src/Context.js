import {createContext,useState} from "react"
import {useNavigate} from "react-router-dom"

export const Context = createContext()

export default function ContextProvider(props){
    const [request,setRequest] = useState("Online")
    const [allFriends,setAllFriends] = useState([])
    const [dms,setDms] = useState([])
    const [username,setUsername] = useState("")
    const [profile,setProfile] = useState("")
    const [showCreateServer,setShowCreateServer] = useState(false)
    const [createServerName,setCreateServerName] = useState(`${username}'s server`)
    const [createServerFile,setCreateServerFile] = useState(null)
    const [serverUsers,setServerUsers] = useState([])
    const [serverWebsocket,setServerWebsocket] = useState(null)
    const [servers,setServers] = useState([])
    const [showInviteUsers,setShowInviteUsers] = useState(false)
    const navigate = useNavigate()
    const token = localStorage.getItem("token")
    async function getUserInformation(){
            let url = `${process.env.REACT_APP_API_BACKEND}/usercredentials`
            let requestOptions = {
                  method: 'GET',
                  headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            }
            let response = await fetch(url,requestOptions)
            let data = await response.json()
            if(response.status === 401){
                navigate("/login")
            }else{
                setUsername(data.username)
                setProfile(data.profile)
            }
        }
    function changeRequest(newRequest){
        setRequest(newRequest)
    }
    async function getDms(){
            const url = `${process.env.REACT_APP_API_BACKEND}/dms`
            const requestOptions = {
                  method: 'GET',
                  headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            }
            const response = await fetch(url,requestOptions)
            const data = await response.json()
            if(response.status === 401){
                navigate("/login")
            }else{
                setDms(data)
            }
        }
    function changeServerWebsocket(websocket){
        setServerWebsocket(websocket)
    }
    function changeDmStatus(username,status){
        if(dms){
            setDms(Dms => (
                Dms.map(dm => (
                    dm.username === username ? {...dm,status:status} : dm
                ))
            ))
        }
    }
    function newProfile(file){
        setProfile(file)
    }
    function changeDmProfile(username,messageProfile){
        if(dms){
            setDms(Dms => (
                Dms.map(dm => (
                    dm.username === username ? {...dm,profile:messageProfile} : dm
                ))
            ))
        }
    }
    async function getAllFriends(){
            const url = `${process.env.REACT_APP_API_BACKEND}/friends`
                    let requestOptions = {
                        method: 'GET',
                        headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token}
                    }
            const response = await fetch(url,requestOptions)
            const data = await response.json()
            if(response.status === 401){
                navigate("/login")
            }else{
                setAllFriends(data)
            }
        }
   function changeFriendStatus(username,changeStatus){
        if(allFriends){
            setAllFriends(AllFriends => (
                AllFriends.map(friend => (
                    friend.username === username ? {...friend,status:changeStatus} : friend
                ))
            ))
        }
   }
   function changeFriendProfile(username,messageProfile){
        setAllFriends(AllFriends => (
            AllFriends.map(friend => (
                friend.username === username ? {...friend,profile:messageProfile} : friend
            ))
        ))
   }
   async function deleteFriend(event,user){
        event.stopPropagation()
        const url = `${process.env.REACT_APP_API_BACKEND}/friend`
        const requestOptions = {
            method: 'DELETE',
            headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            body:JSON.stringify({"username":user})
        }
        const response = await fetch(url,requestOptions)
        setAllFriends(AllFriends => (
            AllFriends.filter(friend => friend.username !== user)
        ))
    }
    function changeShowServer(){
        setShowCreateServer(ShowCreateServer => !ShowCreateServer)
    }
    function changeServerName(value){
        setCreateServerName(value)
    }
    function changeServerFile(event){
        const file = event.target.files[0]
        if(file){
            const reader = new FileReader()
            reader.onload = () => {
                setCreateServerFile(reader.result)
            }
            reader.readAsDataURL(file)
        }
    }
    function resetServerFile(){
        setCreateServerFile(null)
    }
    async function getServers(){
            const url = `${process.env.REACT_APP_API_BACKEND}/servers`
            const requestOptions = {
                  method: 'GET',
                  headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            }
            const response = await fetch(url,requestOptions)
            const data = await response.json()
            if(response.status === 401){
                navigate("/login")
            }else{
                setServers(data)
            }
        }
    function changeShowInviteUsers(){
        setShowInviteUsers(ShowInviteUsers => !ShowInviteUsers)
    }
    async function getServerUsers(id){
            const url = `${process.env.REACT_APP_API_BACKEND}/server/users/` + id
            const requestOptions = {
                  method: 'GET',
                  headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
            }
            const response = await fetch(url,requestOptions)
            const data = await response.json()
            if(response.status === 401){
                navigate("/login")
            }else{
                setServerUsers(data)
            }
    }
    function updateServerUsersStatus(username,status){
        if(serverUsers){
            setServerUsers(ServerUsers => (
                ServerUsers.map(user => (
                    user.username === username ? {...user,status:status} : user
                ))
            ))
        }
    }
    return (
        <Context.Provider value={{request,changeRequest,dms,getDms,username,profile,getUserInformation,changeDmStatus,newProfile,changeDmProfile,allFriends,getAllFriends,changeFriendStatus,deleteFriend,changeFriendProfile,showCreateServer,changeShowServer,
                            createServerFile,createServerName,changeServerName,changeServerFile,resetServerFile,servers,getServers,showInviteUsers,changeShowInviteUsers,serverUsers,getServerUsers,serverWebsocket,changeServerWebsocket,updateServerUsersStatus}}>
            {props.children}
        </Context.Provider>
    )
}
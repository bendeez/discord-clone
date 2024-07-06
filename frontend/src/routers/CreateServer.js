import "./CreateServer.css"
import {useContext} from "react"
import {Context} from "../Context.js"

export default function CreateServer(){
    const {changeShowServer,createServerFile,createServerName,changeServerFile,changeServerName,getServers} = useContext(Context)
    const token = localStorage.getItem("token")
    async function serverSubmit(event){
        event.preventDefault()
        const url = `${process.env.REACT_APP_API_BACKEND}/server`
        const requestBody = createServerFile ? {"name":createServerName,"profile":createServerFile} : {"name":createServerName}
        console.log(requestBody)
        const requestOptions = {
              method: 'POST',
              headers:{'Content-Type': 'application/json',"Authorization":"Bearer " + token},
              body:JSON.stringify(requestBody)
        }
        const response = await fetch(url,requestOptions)
        changeShowServer()
        getServers()
    }
    return(
        <div className="create-server-modal">
            <p>Customize your server</p>
            <form className="create-server-form" onSubmit={serverSubmit}>
                <label for="create-server-file">
                    {createServerFile ? (
                        <img src={createServerFile} className="create-server-file-preview"/>
                    ) : (
                        <div className="create-server-file-label"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-camera"><path d="M23 19a2 2 0 0 1-2 2H3a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h4l2-3h6l2 3h4a2 2 0 0 1 2 2z"></path><circle cx="12" cy="13" r="4"></circle></svg></div>
                    )
                    }
                </label>
                <input type="file" id="create-server-file" className="create-server-file-input" onChange={changeServerFile}/>
                <label for="create-server-text-input" className="create-server-text-label">SERVER NAME</label>
                <input type="text" id="create-server-text-input" className="create-server-text-input" value={createServerName} onChange={(e) => changeServerName(e.target.value)} required/>
                <button className="create-server-button">Create</button>
            </form>
        </div>
    )
}
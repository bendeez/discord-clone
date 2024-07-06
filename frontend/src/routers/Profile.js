import "./Profile.css"
import {useContext} from "react"
import {Context} from "../Context.js"

export default function Profile(){
    const {username,profile,newProfile} = useContext(Context)
    const token = localStorage.getItem("token")
    async function changeProfile(event){
        const file = event.target.files[0]
        const formData = new FormData()
        formData.append("file",file)
        const url = `${process.env.REACT_APP_API_BACKEND}/profilepicture`
        const requestOptions = {
              method: 'PUT',
              headers:{"Authorization":"Bearer " + token},
              body:formData
        }
        const response = await fetch(url,requestOptions)
        const data = await response.json()
        newProfile(data.profile)
    }
    return(
        <div class="profile-container" id="profile-container">
            <div class="profile-container-top">
                <img src={profile} class="profile-image"/>
                <form class="change-profile">
                    <label for="change-profile-input"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-edit-2"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path></svg></label>
                    <input type="file" name="profile" id="change-profile-input" onChange={changeProfile}/>
                </form>
            </div>
            <p>{username}</p>
        </div>
    )
}
import {BrowserRouter,Routes,Route} from "react-router-dom"
import Home from "./routers/Home.js"
import Login from "./routers/Login.js"
import Register from "./routers/Register.js"
import Requests from "./routers/requests/Requests.js"
import Dm from "./routers/Dm.js"
import Server from "./routers/Server.js"
import ContextProvider from "./Context.js"

function App() {
  return (
    <div>
        <BrowserRouter>
            <ContextProvider>
                <Routes>
                    <Route path="/login" element={<Login/>}/>
                    <Route path="/register" element={<Register/>}/>
                    <Route path="/" element={<Home/>}>
                        <Route index element={<Requests/>}/>
                        <Route path="/dm/:id" element={<Dm/>}/>
                        <Route path="/server/:id" element={<Server/>}/>
                    </Route>
                </Routes>
            </ContextProvider>
        </BrowserRouter>
    </div>
  );
}

export default App;

import { Link, useLocation } from "react-router-dom";
import { useNavigate } from "react-router-dom";

import Box from "@mui/material/Box";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";


export default function Navbar(props) {
  const { content } = props;
  const location = useLocation();
  const path = location.pathname;
  const navigate = useNavigate();

  const logoutUser = () => {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    navigate("/");
  };

  return (
          <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static">
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
             <Box sx={{ overflow: "auto" }}>

                 {/* Menu*/}
           <List  sx={{ display: "flex" }}>
             <ListItem key={1} disablePadding>
               <ListItemButton
                 component={Link}
                to="/search"
                selected={"/search" === path}
              >
                 <ListItemText primary={"Search"} />
               </ListItemButton>
             </ListItem>

             <ListItem key={2} disablePadding>
               <ListItemButton
                 component={Link}
                 to="/upload"
                 selected={"/upload" === path}
               >
                 <ListItemText primary={"Upload"} />
               </ListItemButton>
             </ListItem>

             <ListItem key={3} disablePadding>
               <ListItemButton
                 component={Link}
                 to="/help"
                 selected={"/help" === path}
               >
                 <ListItemText primary={"Help"} />
               </ListItemButton>
             </ListItem>
           </List>
         </Box>

            <Box>
                                              <ListItem key={4} disablePadding>
               <ListItemButton onClick={logoutUser}>
                 <ListItemText primary={"Logout"} />
               </ListItemButton>
             </ListItem>
            </Box>


        </Toolbar>
      </AppBar>
                    <Box component="main" sx={{ flexGrow: 1, p: 3 }}>
        <Toolbar />
            {content}
      </Box>
    </Box>
  );
}

import { useState } from "react";
import css from "./stream_table_header.module.css";

export default function StreamTableHeader(){
  const [showHideFiel, setShowHideField] = useState(false);
  function toggleHideDropDown(){
    let dropdownUl = document.getElementById("hide-fields-list")!;
    setShowHideField(prev=>!prev);
  }

  return (
    <div className={`${css.stream_table_header_main_container}`}>
      <div className={`${css.stream_table_header_fn_row}`}>
        <div  id="hide-fields-dropdown" 
              className={`nav-link dropdown-toggle idaes-nav-button ${css.hideFieldBtn}`} 
              data-toggle="dropdown" 
              aria-haspopup="true" 
              aria-expanded="false" 
              onClick={toggleHideDropDown}
        >
          <span>Hide Fields</span>
          <ul id="hide-fields-list" 
              className={`dropdown-menu checkbox-menu ${css.dropdownMenu}`}
              style={{display : showHideFiel ? "block" : "none"}}
          >
            {/* table cell is generate base on model */}
          </ul>
        </div>
      </div>
      
      {/* table cell is generate base on model */}
      <div id="existing-variable-types" className={`streamtable-vartype-panel ${css.streamtable_vartype_panel}`}></div>
    </div>
  )
}
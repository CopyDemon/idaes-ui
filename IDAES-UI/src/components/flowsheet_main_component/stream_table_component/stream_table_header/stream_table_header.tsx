import { useContext, useState } from "react";
import { AppContext } from '../../../../context/appMainContext';
import { minimizePanel } from "../../flowsheet_component/flowsheet_functions/universal_functions";
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMinus } from '@fortawesome/free-solid-svg-icons';
import css from "./stream_table_header.module.css";

export default function StreamTableHeader(){
  const {setPanelState} = useContext(AppContext);
  const [showHideFiel, setShowHideField] = useState(false);
  function toggleHideDropDown(){
    let dropdownUl = document.getElementById("hide-fields-list")!;
    setShowHideField(prev=>!prev);
  }

  return (
    <div className={`${css.stream_table_header_main_container}`}>
      <div className={`mb-md pd-md ${css.stream_table_header_fn_row}`}>
        <p className={css.stream_table_title}>STREAM TABLE</p>
        <div id="stream_table_header_right_container" className={`${css.stream_table_right_container}`}>
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
          <span 
            id="minimize-flowsheet-panel-btn"
            className={`pd-sm ${css.flowsheet_header_icon_container} 
            ${css.flowsheetHeader_small_icon}`}
            onClick={()=>minimizePanel('streamTable', setPanelState)}
          >
            <FontAwesomeIcon icon={faMinus} />
          </span>
        </div>
      </div>
      
      {/* table cell is generate base on model */}
      <div id="existing-variable-types" className="pd-md streamtable-vartype-panel"></div>
    </div>
  )
}
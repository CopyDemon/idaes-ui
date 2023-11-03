import { useContext, useRef } from "react";
import { AppContext } from "../../../context/appMainContext";

import css from "./flowsheet.module.css";

declare var joint: any;
declare var paper: any;

export default function Flowsheet(){
  const {panelState, cells} = useContext(AppContext);
  const isShowFlowsheet = panelState["fv"].show;

  return(
    <>
      <h1>{import.meta.env.VITE_TEST}</h1>
      {
        isShowFlowsheet &&
        <section id="fvContainer" className={`${css.fvContainer}`}>
          <div id="fv" className={`${css.fv}`}></div>
        </section>
      }
    </>
  )
}
import styles from './StyleRoaster.module.css'

import {Image} from '../Image/Image'

import { styleImages } from './styles'


export const StyleRoaster = (props) => {


    return (

<div>
    <h2>{props.type=="fg"?"foreground style":"background style" }</h2> 
        <div class={styles.container}>  
            {styleImages.map(style => <Image type={props.type} imageName={style.styleName} image={style.styleImage}/>)}
        </div>
</div>

)

}
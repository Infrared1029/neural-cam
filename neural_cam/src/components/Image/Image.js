
import styles from './Image.module.css'

const setStyle = async (style, type) => {
    await fetch(`http://localhost:8000/set_${type}_style/${style}`)
  }
  


export const Image = (props) => {

  // console.log(props)

    return (
    <div class={styles.styleImageContainer}>
          <img src={props.image} class={styles.styleImage} onClick={() => setStyle(props.imageName, props.type)}></img>
    </div>
    )

}
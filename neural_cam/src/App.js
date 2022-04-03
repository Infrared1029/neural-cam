import styles from './App.module.css'



import { StyleRoaster } from './components/StyleRoaster/StyleRoaster'


const closeCam = async () => {
  await fetch('http://localhost:8000/turn_cam_off')
}

const resetStyles = async () => {
  await fetch('http://localhost:8000/reset_styles')
}

function App() {
  return (
    <div class={styles.container}>
      <h1>Neural Style Transfer Demo</h1>

      <div class={styles.cameraContainer}>
        <img class={styles.video} src='http://localhost:8000/'></img>
        <button class={styles.closeButton} onClick={closeCam}> Close </button>
        <button class={styles.resetButton} onClick={resetStyles}> reset styles </button>

      </div>

      <div class={styles.stylesContainer}> 
        <StyleRoaster type='fg'/>
        <StyleRoaster type='bg'/>
      </div>

        {/* <button class={styles.CloseButton} onClick={closeCam}> Close </button> */}
       
      </div>
   
  );
}

export default App;

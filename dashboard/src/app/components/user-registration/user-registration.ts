import { Component, OnInit, ViewChild, ElementRef, OnDestroy } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { ApiService } from '../../services/api.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-user-registration',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './user-registration.html',
  styleUrl: './user-registration.css',
})
export class UserRegistration implements OnInit, OnDestroy {
  @ViewChild('video') videoElement!: ElementRef<HTMLVideoElement>;
  @ViewChild('canvas') canvasElement!: ElementRef<HTMLCanvasElement>;

  regForm!: FormGroup;
  stream: MediaStream | null = null;
  
  // FaceID State
  isCapturing = false;
  registrationComplete = false;
  currentPoseIndex = 0;
  poses = ['frente', 'izquierda', 'derecha', 'arriba', 'abajo'];
  poseMessages: {[key: string]: string} = {
    'frente': 'Mira fijo a la cámara',
    'izquierda': 'Gira la cabeza a la IZQUIERDA',
    'derecha': 'Gira la cabeza a la DERECHA',
    'arriba': 'Mira hacia ARRIBA',
    'abajo': 'Mira hacia ABAJO'
  };
  capturedBlobs: { [key: string]: Blob } = {};
  progress = 0;

  constructor(
    private fb: FormBuilder,
    private api: ApiService,
    private router: Router
  ) {
    this.regForm = this.fb.group({
      nombre: ['', Validators.required],
      apellidos: [''],
      dni: ['', [Validators.required, Validators.pattern('^[0-9]{8,10}$')]],
      celular: [''],
      correo: ['', [Validators.email]],
    });
  }

  get currentPose() { return this.poses[this.currentPoseIndex]; }
  get poseMessage() { return this.poseMessages[this.currentPose]; }

  async ngOnInit() {
    await this.initCamera();
  }

  ngOnDestroy() {
    this.stopCamera();
  }

  async initCamera() {
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 400, height: 400, facingMode: 'user' } 
      });
      this.videoElement.nativeElement.srcObject = this.stream;
    } catch (err) {
      console.error('Error al acceder a la cámara:', err);
    }
  }

  stopCamera() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
  }

  calculateOffset() {
    const circumference = 2 * Math.PI * 48; // 301.59
    return circumference - (this.progress / 100) * circumference;
  }

  async startFaceID() {
    if (this.regForm.invalid) {
      alert('Por favor, completa los datos del formulario primero.');
      return;
    }
    this.isCapturing = true;
    this.currentPoseIndex = 0;
    this.progress = 0;
    this.nextStep();
  }

  private nextStep() {
    if (this.currentPoseIndex >= this.poses.length) {
      this.isCapturing = false;
      this.registrationComplete = true;
      this.progress = 100;
      return;
    }

    let stepProgress = 0;
    const interval = setInterval(() => {
      stepProgress += 5;
      this.progress = (this.currentPoseIndex * 20) + (stepProgress / 5);
    if (stepProgress >= 100) {
        clearInterval(interval);
        const poseToCapture = this.currentPose; // Guardar el pose actual
        this.captureAngle(poseToCapture);
        this.currentPoseIndex++;
        setTimeout(() => this.nextStep(), 500);
      }
    }, 100);
  }

  private captureAngle(pose: string) {
    const video = this.videoElement.nativeElement;
    const canvas = this.canvasElement.nativeElement;
    const context = canvas.getContext('2d');

    if (context) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      canvas.toBlob((blob) => {
        if (blob) this.capturedBlobs[pose] = blob; // Usar el pose guardado
      }, 'image/jpeg', 0.8);
    }
  }

  resetFaceID() {
    this.registrationComplete = false;
    this.isCapturing = false;
    this.currentPoseIndex = 0;
    this.progress = 0;
    this.capturedBlobs = {};
  }

  onSubmit() {
    if (this.regForm.valid && this.registrationComplete) {
      const formData = new FormData();
      const rawValues = this.regForm.value;
      
      Object.keys(rawValues).forEach(key => {
        if (rawValues[key]) formData.append(key, rawValues[key]);
      });
      
      // Enviar todos los ángulos: foto_frente, foto_izquierda, etc.
      const userPrefix = rawValues.usuario || rawValues.nombre.split(' ')[0].toLowerCase();
      Object.keys(this.capturedBlobs).forEach(angle => {
        formData.append(`foto_${angle}`, this.capturedBlobs[angle], `${userPrefix}_${angle}.jpg`);
      });

      this.api.registerUser(formData).subscribe({
        next: (res) => {
          alert('¡Usuario registrado con éxito con Biometría FaceID!');
          this.router.navigate(['/dashboard']);
        },
        error: (err) => {
          console.error('Error de registro:', err);
          const msg = err.error?.detail || err.message || 'Error desconocido en el servidor';
          alert('Error al registrar usuario: ' + msg);
        }
      });
    }
  }
}

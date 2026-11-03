// Web Audio API Synthesizer for Authentic Minecraft Sound Effects (Raid Horn, Cannon Explosions, Anvil, Dragons)

class SoundSynthesizer {
  private ctx: AudioContext | null = null;

  private getContext(): AudioContext | null {
    if (typeof window === 'undefined') return null;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  /**
   * Raid Horn: ominous low brass war horn blast (Minecraft Pillager Raid / Siege alert)
   */
  public playRaidHorn() {
    const ctx = this.getContext();
    if (!ctx) return;
    try {
      const now = ctx.currentTime;
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();

      osc1.type = 'sawtooth';
      osc2.type = 'triangle';

      // Pitch sweep
      osc1.frequency.setValueAtTime(140, now);
      osc1.frequency.exponentialRampToValueAtTime(120, now + 1.2);
      osc2.frequency.setValueAtTime(142, now);
      osc2.frequency.exponentialRampToValueAtTime(122, now + 1.2);

      // Low pass filter to create brass horn warmth
      const filter = ctx.createBiquadFilter();
      filter.type = 'lowpass';
      filter.frequency.setValueAtTime(450, now);
      filter.frequency.linearRampToValueAtTime(320, now + 1.2);

      gain.gain.setValueAtTime(0.01, now);
      gain.gain.linearRampToValueAtTime(0.25, now + 0.15);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.4);

      osc1.connect(filter);
      osc2.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 1.45);
      osc2.stop(now + 1.45);
    } catch (e) {
      console.warn('Audio synthesis error:', e);
    }
  }

  /**
   * Cannon / TNT Explosion: heavy impact with low-end rumble and debris
   */
  public playExplosion() {
    const ctx = this.getContext();
    if (!ctx) return;
    try {
      const now = ctx.currentTime;

      // 1. White noise burst for blast
      const bufferSize = ctx.sampleRate * 0.8;
      const buffer = ctx.createBuffer(1, bufferSize, ctx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) {
        data[i] = Math.random() * 2 - 1;
      }

      const noise = ctx.createBufferSource();
      noise.buffer = buffer;

      const noiseFilter = ctx.createBiquadFilter();
      noiseFilter.type = 'lowpass';
      noiseFilter.frequency.setValueAtTime(900, now);
      noiseFilter.frequency.exponentialRampToValueAtTime(80, now + 0.7);

      const noiseGain = ctx.createGain();
      noiseGain.gain.setValueAtTime(0.35, now);
      noiseGain.gain.exponentialRampToValueAtTime(0.001, now + 0.75);

      noise.connect(noiseFilter);
      noiseFilter.connect(noiseGain);
      noiseGain.connect(ctx.destination);

      // 2. Sub-bass punch oscillator
      const sub = ctx.createOscillator();
      const subGain = ctx.createGain();
      sub.type = 'sine';
      sub.frequency.setValueAtTime(110, now);
      sub.frequency.exponentialRampToValueAtTime(30, now + 0.45);

      subGain.gain.setValueAtTime(0.4, now);
      subGain.gain.exponentialRampToValueAtTime(0.001, now + 0.5);

      sub.connect(subGain);
      subGain.connect(ctx.destination);

      noise.start(now);
      sub.start(now);
      noise.stop(now + 0.8);
      sub.stop(now + 0.5);
    } catch (e) {
      console.warn('Audio synthesis error:', e);
    }
  }

  /**
   * Ender Dragon Growl: deep resonance for 2-hour assault start
   */
  public playAssaultAlert() {
    const ctx = this.getContext();
    if (!ctx) return;
    try {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      const filter = ctx.createBiquadFilter();

      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(80, now);
      osc.frequency.linearRampToValueAtTime(55, now + 0.8);

      filter.type = 'bandpass';
      filter.frequency.setValueAtTime(180, now);
      filter.Q.value = 3;

      gain.gain.setValueAtTime(0.01, now);
      gain.gain.linearRampToValueAtTime(0.3, now + 0.1);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.1);

      osc.connect(filter);
      filter.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 1.15);
    } catch (e) {
      console.warn('Audio synthesis error:', e);
    }
  }

  /**
   * Block Anvil / Camp Claim: metallic placement sound
   */
  public playAnvilChime() {
    const ctx = this.getContext();
    if (!ctx) return;
    try {
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(880, now);
      osc.frequency.exponentialRampToValueAtTime(440, now + 0.2);

      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now);
      osc.stop(now + 0.35);
    } catch (e) {
      console.warn('Audio synthesis error:', e);
    }
  }

  /**
   * Beacon Beam Activation: ethereal crystal harmonic hum rising into the sky
   */
  public playBeaconActivate() {
    const ctx = this.getContext();
    if (!ctx) return;
    try {
      const now = ctx.currentTime;
      const osc1 = ctx.createOscillator();
      const osc2 = ctx.createOscillator();
      const gain = ctx.createGain();

      osc1.type = 'sine';
      osc2.type = 'triangle';

      osc1.frequency.setValueAtTime(261.63, now); // C4
      osc1.frequency.exponentialRampToValueAtTime(523.25, now + 0.6); // C5
      osc1.frequency.exponentialRampToValueAtTime(1046.50, now + 1.2); // C6

      osc2.frequency.setValueAtTime(329.63, now); // E4
      osc2.frequency.exponentialRampToValueAtTime(659.25, now + 0.6); // E5
      osc2.frequency.exponentialRampToValueAtTime(1318.51, now + 1.2); // E6

      gain.gain.setValueAtTime(0.01, now);
      gain.gain.linearRampToValueAtTime(0.28, now + 0.2);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 1.5);

      osc1.connect(gain);
      osc2.connect(gain);
      gain.connect(ctx.destination);

      osc1.start(now);
      osc2.start(now);
      osc1.stop(now + 1.55);
      osc2.stop(now + 1.55);
    } catch (e) {
      console.warn('Audio synthesis error:', e);
    }
  }

  /**
   * Challenge / Conquest Triumph: triumphant fanfare chord
   */
  public playTriumph() {
    const ctx = this.getContext();
    if (!ctx) return;
    try {
      const now = ctx.currentTime;
      const freqs = [523.25, 659.25, 783.99, 1046.50]; // C Major arpeggio
      freqs.forEach((freq, idx) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'triangle';
        osc.frequency.setValueAtTime(freq, now + idx * 0.08);

        gain.gain.setValueAtTime(0.01, now + idx * 0.08);
        gain.gain.linearRampToValueAtTime(0.18, now + idx * 0.08 + 0.04);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 1.2);

        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start(now + idx * 0.08);
        osc.stop(now + 1.25);
      });
    } catch (e) {
      console.warn('Audio synthesis error:', e);
    }
  }
}

export const soundFx = new SoundSynthesizer();


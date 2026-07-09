'use client';

import React from 'react';
import styles from './Hero.module.css';

interface HeroProps {
  title: string;
  subtitle?: string;
  ctaText?: string;
  onCtaClick?: () => void;
}

const Hero: React.FC<HeroProps> = ({ title, subtitle, ctaText, onCtaClick }) => {
  return (
    <section className={styles.hero} aria-labelledby="hero-title">
      <div className={styles.content}>
        <h1 id="hero-title" className={styles.title}>
          {title}
        </h1>
        {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
        {ctaText && (
          <button
            onClick={onCtaClick}
            className={styles.cta}
            aria-label={ctaText}
          >
            {ctaText}
          </button>
        )}
      </div>
    </section>
  );
};

export default Hero;
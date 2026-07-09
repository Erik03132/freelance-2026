'use client';

import React, { ButtonHTMLAttributes, forwardRef } from 'react';
import styles from './Button.module.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'text';
  size?: 'small' | 'medium' | 'large';
  fullWidth?: boolean;
  loading?: boolean;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'medium',
      fullWidth = false,
      loading = false,
      className = '',
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const variantClass = styles[`button--${variant}`];
    const sizeClass = styles[`button--${size}`];
    const widthClass = fullWidth ? styles['button--full'] : '';
    const loadingClass = loading ? styles['button--loading'] : '';
    const disabledClass = disabled ? styles['button--disabled'] : '';

    return (
      <button
        ref={ref}
        className={`${styles.button} ${variantClass} ${sizeClass} ${widthClass} ${loadingClass} ${disabledClass} ${className}`}
        disabled={disabled || loading}
        aria-busy={loading}
        {...props}
      >
        {loading && <span className={styles.loader} aria-hidden="true" />}
        <span className={styles.content}>{children}</span>
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
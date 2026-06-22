# React & Frontend Patterns

## Component Patterns
- **Composition > Inheritance** — `<Card><CardHeader/><CardBody/></Card>`
- **Compound Components** — Context + Provider для связанных компонентов
- **Render Props** — для переиспользуемой логики с custom rendering

## Custom Hooks
```typescript
// Debounce для поиска
function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)
  useEffect(() => {
    const handler = setTimeout(() => setDebouncedValue(value), delay)
    return () => clearTimeout(handler)
  }, [value, delay])
  return debouncedValue
}

// Toggle
function useToggle(initial = false): [boolean, () => void] {
  const [value, setValue] = useState(initial)
  const toggle = useCallback(() => setValue(v => !v), [])
  return [value, toggle]
}
```

## Performance Optimization
```typescript
// Memoization
const sorted = useMemo(() => items.sort((a, b) => b.rank - a.rank), [items])
const handleSearch = useCallback((q: string) => setQuery(q), [])
const PureCard = React.memo(({ item }) => <div>{item.name}</div>)

// Code Splitting
const HeavyChart = lazy(() => import('./HeavyChart'))
<Suspense fallback={<Skeleton />}><HeavyChart /></Suspense>

// Virtualization
import { useVirtualizer } from '@tanstack/react-virtual'
```

## Error Boundaries
```typescript
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null }
  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }
  render() {
    if (this.state.hasError) {
      return <div className="error-fallback">
        <h2>Что-то пошло не так</h2>
        <button onClick={() => this.setState({ hasError: false })}>Попробовать снова</button>
      </div>
    }
    return this.props.children
  }
}
```

## Animations (Framer Motion)
```typescript
import { motion, AnimatePresence } from 'framer-motion'

<AnimatePresence>
  {items.map(item => (
    <motion.div
      key={item.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
    >
      <ItemCard item={item} />
    </motion.div>
  ))}
</AnimatePresence>
```

## Accessibility (a11y)
- Keyboard navigation на всех интерактивных элементах
- ARIA-атрибуты: `role`, `aria-expanded`, `aria-modal`
- Focus management: сохранение и восстановление фокуса
- Touch targets: минимум 44x44px
- Контрастность: WCAG AA (4.5:1)

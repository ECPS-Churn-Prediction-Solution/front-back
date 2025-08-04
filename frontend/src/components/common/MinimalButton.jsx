import styled from 'styled-components';

const MinimalButton = ({ children, ...props }) => (
  <Btn {...props}>{children}</Btn>
);

const Btn = styled.button`
  border: 1px solid #222;
  background: none;
  color: #222;
  border-radius: 999px;
  padding: 0.5rem 1.5rem;
  font-weight: bold;
  font-size: 1rem;
  transition: background 0.2s, color 0.2s;
  &:hover {
    background: #222;
    color: #fff;
  }
`;

export default MinimalButton;
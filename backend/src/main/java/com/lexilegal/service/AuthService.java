package com.lexilegal.service;

import com.lexilegal.dto.request.LoginRequest;
import com.lexilegal.dto.request.RegisterRequest;
import com.lexilegal.dto.response.AuthResponse;
import com.lexilegal.dto.response.UserProfileResponse;
import com.lexilegal.entity.User;
import com.lexilegal.exception.DuplicateEmailException;
import com.lexilegal.exception.RateLimitExceededException;
import com.lexilegal.repository.UserRepository;
import com.lexilegal.security.JwtTokenProvider;
import com.lexilegal.security.LoginRateLimiter;
import com.lexilegal.security.UserPrincipal;
import org.springframework.security.authentication.BadCredentialsException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;
    private final LoginRateLimiter rateLimiter;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtTokenProvider tokenProvider,
            LoginRateLimiter rateLimiter) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.tokenProvider = tokenProvider;
        this.rateLimiter = rateLimiter;
    }

    @Transactional
    public AuthResponse register(RegisterRequest request) {
        String normalizedEmail = request.getEmail().toLowerCase().trim();

        if (userRepository.existsByEmail(normalizedEmail)) {
            throw new DuplicateEmailException("an account with this email already exists");
        }

        String passwordHash = passwordEncoder.encode(request.getPassword());
        User user = new User(normalizedEmail, passwordHash, request.getFullName().trim());
        User savedUser = userRepository.save(user);

        UserPrincipal principal = UserPrincipal.create(savedUser);
        String token = tokenProvider.generateToken(principal);

        return new AuthResponse(token, UserProfileResponse.fromEntity(savedUser));
    }

    @Transactional(readOnly = true)
    public AuthResponse login(LoginRequest request, String clientIp) {
        if (!rateLimiter.tryAcquire(clientIp)) {
            throw new RateLimitExceededException("too many login attempts; please try again later");
        }

        String normalizedEmail = request.getEmail().toLowerCase().trim();
        User user = userRepository.findByEmail(normalizedEmail)
                .orElseThrow(() -> new BadCredentialsException("invalid email or password"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new BadCredentialsException("invalid email or password");
        }

        rateLimiter.reset(clientIp);

        UserPrincipal principal = UserPrincipal.create(user);
        String token = tokenProvider.generateToken(principal);

        return new AuthResponse(token, UserProfileResponse.fromEntity(user));
    }
}
